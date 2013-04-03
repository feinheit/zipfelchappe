import json
from functools import wraps

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect as _redirect
from django.views.generic import ListView, DetailView, FormView, TemplateView

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from feincms.content.application.models import app_reverse
from feincms.module.mixins import ContentView

from . import forms, app_settings
from .emails import send_pledge_completed_message
from .models import Project, Pledge, Backer, Category, Update, MailTemplate
from .utils import get_object_or_none


#-----------------------------------
# decorators and mixins
#-----------------------------------

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
    return app_reverse(view_name, 'zipfelchappe.urls', args=args, kwargs=kwargs)


def redirect(view_name, *args, **kwargs):
    """ Imitate django redirect() within our app context """
    try:
        return _redirect(reverse(view_name, *args, **kwargs))
    except NoReverseMatch:
        return _redirect(view_name, *args, **kwargs)


#-----------------------------------
# views
#-----------------------------------

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
        return Project.objects.online().select_related()

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        context['disqus_shortname'] = app_settings.DISQUS_SHORTNAME
        context['updates'] = self.get_object().updates.filter(
            status=Update.STATUS_PUBLISHED
        )

        context['thank_you'] = 'thank_you' in self.request.GET
        if 'completed_pledge_id' in self.request.session:
            pledge_id = self.request.session['completed_pledge_id']
            context['pledge'] = get_object_or_none(Pledge, pk=pledge_id)

        return context


class UpdateDetailView(FeincmsRenderMixin, DetailView):
    """ Just a simple view of one project update for preview purposes """

    context_object_name = 'update'
    model = Update

    def get_context_data(self, **kwargs):
        context = super(UpdateDetailView, self).get_context_data(**kwargs)
        context['project'] = self.get_object().project
        return context


def project_back_form(request, slug):
    """ The main form to back a project. A lot of the magic here comes from
        BackProjectForm including all validation. The main job of this view is
        to save the pledge_id in the session and redirect to backer_authenticate
    """

    project = get_object_or_404(Project, slug=slug)

    if not project.is_active:
        messages.info(request, _('This project has ended and does not accept'
                                 ' pledges anymore.'))
        return redirect('zipfelchappe_project_detail',
            kwargs={'slug': project.slug})

    session_pledge = get_session_pledge(request)
    form_kwargs = {'project': project}

    if session_pledge and session_pledge.project == project:
        form_kwargs.update({'instance': session_pledge})

    if request.method == 'POST':
        form = forms.BackProjectForm(request.POST, **form_kwargs)

        if form.is_valid():
            pledge = form.save()
            request.session['pledge_id'] = pledge.id
            return redirect('zipfelchappe_backer_authenticate')
    else:
        form = forms.BackProjectForm(**form_kwargs)

    return ('zipfelchappe/project_back_form.html', {
        'project': project,
        'form': form,
    })


@requires_pledge
def backer_authenticate(request, pledge):
    """ Show login view if user is not authenticated.

        Once the user is authenticated, save user to the current pledge and
        redirect to the selected payment provider.
    """

    payment_view = 'zipfelchappe_%s_payment' % pledge.provider

    if request.user.is_authenticated():
        backer, created = Backer.objects.get_or_create(user=request.user)
        pledge.backer = backer
        pledge.save()
        return redirect(payment_view)
    else:
        return ('zipfelchappe/backer_authenticate_form.html', {
            'pledge': pledge,
            'project': pledge.project,
            'login_form': AuthenticationForm(),
            'register_form': forms.RegisterUserForm(),
        })


# TODO: This view should be removed
@requires_pledge_cbv
class BackerLoginView(FeincmsRenderMixin, PledgeContextMixin, FormView):
    """ A very simple login for normal django users """
    form_class = AuthenticationForm
    permanent = False
    template_name = "zipfelchappe/backer_login_form.html"

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect('zipfelchappe_backer_authenticate')


# TODO: This view should be removed
@requires_pledge_cbv
class BackerRegisterView(FeincmsRenderMixin, PledgeContextMixin, FormView):
    """ A very simple registratation view for normal django users """
    form_class = forms.RegisterUserForm
    permanent = False
    template_name = "zipfelchappe/backer_register_form.html"

    def form_valid(self, form):
        user = form.save()
        password = form.cleaned_data['password1']
        user = authenticate(username=user.username, password=password)
        login(self.request, user)
        return redirect('zipfelchappe_backer_authenticate')


def pledge_thankyou(request):
    """ Send pledge completed message, redirect to thank you page """
    pledge = get_session_pledge(request)

    if not pledge:
        return redirect('zipfelchappe_project_list')
    else:
        send_pledge_completed_message(pledge)
        del request.session['pledge_id']
        request.session['completed_pledge_id'] = pledge.pk
        url = reverse('zipfelchappe_project_detail',  slug=pledge.project.slug)
        return redirect(url + '?thank_you')


def pledge_cancel(request):
    """ Remove current pledge from session """
    pledge = get_session_pledge(request)

    if not pledge:
        return redirect('zipfelchappe_project_list')
    else:
        del request.session['pledge_id']
        messages.info(request, _('Your pledge was canceled'))
        return redirect('zipfelchappe_project_detail', slug=pledge.project.slug)


class PledgeLostView(FeincmsRenderMixin, TemplateView):
    """ Error message showed by @pledge_required if not pledge was found """
    template_name = "zipfelchappe/pledge_lost.html"


@csrf_exempt
@staff_member_required
def send_test_mail(request):
    """ Used in the admin to test mail templates """
    project = get_object_or_404(Project, pk=request.POST.get('project', -1))

    action = request.POST.get('action', None)
    subject = request.POST.get('subject', None)
    template = request.POST.get('template', None)
    recipient = request.POST.get('recipient', None)

    mail_template = MailTemplate(
        project=project,
        action=action,
        subject=subject,
        template=template
    )

    fake_plede = Pledge(
        project=project,
        amount=10,
        backer=Backer(
            _first_name=request.user.first_name,
            _last_name=request.user.last_name,
            _email=recipient
        )
    )

    from smtplib import SMTPException
    try:
        send_pledge_completed_message(fake_plede, mail_template)
        success = True
    except SMTPException:
        success = False

    return HttpResponse(json.dumps({
        'success': success,
    }), mimetype="application/json")
