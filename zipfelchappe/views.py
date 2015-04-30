from functools import wraps
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.shortcuts import get_object_or_404, redirect as _redirect
from django.views.generic import ListView, DetailView, TemplateView

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from feincms.content.application.models import app_reverse
from feincms.module.mixins import ContentView

from . import forms, app_settings
from .emails import send_pledge_completed_message
from .models import Project, Pledge, Backer, Category, Update, Reward
from .utils import get_object_or_none


# -----------------------------------
#  decorators and mixins
# -----------------------------------

def get_session_pledge(request):
    """ returns the last created pledge for the current session or None """

    pledge_id = request.session.get('pledge_id', None)
    if pledge_id:
        return get_object_or_none(Pledge, pk=pledge_id)
    return None


def requires_pledge(func):
    """ Decorator to enforce current pledge as second parameter.
        If no pledge is is found in session, show an error message. """

    @wraps(func)
    def _decorator(request, *args, **kwargs):
        pledge = get_session_pledge(request)
        if pledge:
            return func(request, pledge, *args, **kwargs)
        else:
            return redirect('zipfelchappe_pledge_lost')
    return _decorator


def requires_pledge_cbv(clazz):
    """ Class based decorator to save current pledge in self.pledge """

    orig_dispatch = clazz.dispatch

    def monkey_dispatch(self, request, *args, **kwargs):
        self.pledge = get_session_pledge(request)
        if self.pledge is not None:
            return orig_dispatch(self, request, *args, **kwargs)
        else:
            return redirect('zipfelchappe_pledge_lost')

    clazz.dispatch = monkey_dispatch
    return clazz


class PledgeContextMixin(object):
    """ Mixin to add the current pledge to the template context """

    def get_context_data(self, *args, **kwargs):
        context = super(PledgeContextMixin, self).get_context_data(*args, **kwargs)

        pledge = getattr(self, 'pledge', get_session_pledge(self.request))

        if pledge:
            context.update({
                'pledge': pledge,
                'project': pledge.project
            })

        return context


class FeincmsRenderMixin(object):
    """ This is required to use django template inheritance with CBVs """

    def render_to_response(self, context, **response_kwargs):
        return self.get_template_names(), context


def reverse(view_name, *args, **kwargs):
    """ Reverse within our app context """
    return app_reverse(view_name, app_settings.ROOT_URLS, args=args, kwargs=kwargs)


def redirect(view_name, *args, **kwargs):
    """ Imitate django redirect() within our app context """
    try:
        return _redirect(reverse(view_name, *args, **kwargs))
    except NoReverseMatch:
        return _redirect(view_name, *args, **kwargs)


# -----------------------------------
#  views
# -----------------------------------

class ProjectListView(FeincmsRenderMixin, ListView):
    """ List view of all projects that are active or finished.
        To change pagination count set ZIPFELCHAPPE_PAGINATE_BY in settings.
    """
    context_object_name = "project_list"
    paginate_by = app_settings.PAGINATE_BY
    model = Project

    def get_queryset(self):
        return Project.objects.online().select_related()

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        return context


class ProjectCategoryListView(ProjectListView):
    """ Filtered project list view for only one category """

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        online_projects = Project.objects.online().select_related()
        return online_projects.filter(categories=category)


class ProjectDetailView(FeincmsRenderMixin, ContentView):
    """ Show status, description, updates, backers and comments of a project """

    context_object_name = "project"
    model = Project

    def get_queryset(self):
        # limit queryset to projects that have started.
        return Project.objects.online().select_related('rewards')

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        context['disqus_shortname'] = app_settings.DISQUS_SHORTNAME
        context['updates'] = context['project'].updates.filter(
            status=Update.STATUS_PUBLISHED
        )
        # create a paginated list of backers.
        backers = context['project'].public_pledges
        paginator = Paginator(backers, app_settings.PAGINATE_BACKERS_BY)
        context['backer_count'] = len(backers)
        context['paginator'] = paginator
        page = int(self.request.GET.get('backers-page', 1))
        try:
            context['page_obj'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context['page_obj'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            context['page_obj'] = paginator.page(paginator.num_pages)

        return context


class UpdateDetailView(FeincmsRenderMixin, DetailView):
    """ Just a simple view of one project update for preview purposes """

    context_object_name = 'update'
    model = Update

    def get_context_data(self, **kwargs):
        context = super(UpdateDetailView, self).get_context_data(**kwargs)
        context['project'] = self.get_object().project
        return context


class ProjectDetailHasBackedView(ProjectDetailView):
    """ This view is called at the end of the backing process. """

    template_name = 'zipfelchappe/project_has_backed.html'

    def get_queryset(self):
        return Project.objects.online()

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailHasBackedView, self).get_context_data(**kwargs)

        if 'completed_pledge_id' in self.request.session:
            pledge_id = self.request.session['completed_pledge_id']
            del self.request.session['completed_pledge_id']
            context['pledge'] = get_object_or_none(Pledge, pk=pledge_id)

        return context


def backer_create_view(request, slug):
    """ The main form to back a project. A lot of the magic here comes from
        BackProjectForm including all validation. The main job of this view is
        to save the pledge_id in the session and redirect to backer_authenticate.
        A pledge is created but a user is not yet assigned.
    """
    project = get_object_or_404(Project, slug=slug)
    ExtraForm = project.extraform()

    if project.is_over:
        messages.info(request, _('This project has ended and does not accept'
                                 ' pledges anymore.'))
        return redirect(
            'zipfelchappe_project_detail', slug=project.slug)

    session_pledge = get_session_pledge(request)
    form_kwargs = {'project': project}
    # If the session pledge has already been paid for, ignore it.
    if session_pledge and session_pledge.project == project:
        if session_pledge.status >= session_pledge.FAILED:  # Force a new payment-ID.
            request.session.delete('pledge_id')
        else:
            form_kwargs.update({'instance': session_pledge})

    if request.method == 'POST':
        form = forms.BackProjectForm(request.POST, **form_kwargs)
        extraform = ExtraForm(request.POST, prefix="extra")

        if form.is_valid() and extraform.is_valid():
            pledge = form.save(commit=False)
            pledge.extradata = extraform.clean()
            pledge.save()
            request.session['pledge_id'] = pledge.id
            return redirect(settings.LOGIN_URL)
    else:
        form = forms.BackProjectForm(**form_kwargs)
        extraform = ExtraForm(prefix="extra")

    return ('zipfelchappe/project_back_form.html', {
        'project': project,
        'form': form,
        'extraform': extraform,
    })


@requires_pledge
@login_required
def backer_authenticate(request, pledge):
    """ save user to the current pledge and
        redirect to the selected payment provider.
    """
    payment_view = 'zipfelchappe_%s_payment' % pledge.provider
    backer, created = Backer.objects.get_or_create(user=request.user)
    pledge.backer = backer
    pledge.save()
    return redirect(payment_view)


def pledge_thankyou(request):
    """ Send pledge completed message, redirect to thank you page """
    pledge = get_session_pledge(request)

    if not pledge:
        return redirect('zipfelchappe_project_list')
    else:
        send_pledge_completed_message(pledge)
        del request.session['pledge_id']
        request.session['completed_pledge_id'] = pledge.pk
        url = reverse('zipfelchappe_project_backed',  slug=pledge.project.slug)
        return redirect(url)


def pledge_cancel(request):
    """ Remove current pledge from session """
    pledge = get_session_pledge(request)

    if not pledge:
        return redirect('zipfelchappe_project_list')
    else:
        del request.session['pledge_id']
        pledge.mark_failed()
        messages.info(request, _('Your pledge was canceled'))
        return redirect('zipfelchappe_project_detail', slug=pledge.project.slug)


class PledgeLostView(FeincmsRenderMixin, TemplateView):
    """ Error message showed by @pledge_required if not pledge was found """
    template_name = "zipfelchappe/pledge_lost.html"
