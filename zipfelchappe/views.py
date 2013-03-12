import json
from functools import wraps

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect as _redirect
from django.views.generic import ListView, DetailView, FormView, TemplateView

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from feincms.content.application.models import app_reverse

from . import forms, app_settings
from .emails import send_pledge_completed_message
from .models import Project, Pledge, Category, Update, MailTemplate
from .utils import get_backer_model, use_default_backer_model, get_object_or_none


#-----------------------------------
# decorators and mixins
#-----------------------------------

def get_session_pledge(request):
    pledge_id = request.session.get('pledge_id', None)
    if pledge_id:
        return get_object_or_none(Pledge, pk=pledge_id)
    return None


def requires_pledge(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        pledge = get_session_pledge(request)
        if pledge:
            return func(request, pledge, *args, **kwargs)
        else:
            return redirect('zipfelchappe_pledge_lost')
    return _decorator


def requires_pledge_cbv(clazz):

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

    def render_to_response(self, context, **response_kwargs):
        if 'app_config' in getattr(self.request, '_feincms_extra_context', {}):
            return self.get_template_names(), context

        return super(FeincmsRenderMixin, self).render_to_response(
            context, **response_kwargs)


def feincms_render(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        try:
            template_name, context = response
            if 'app_config' in getattr(request, '_feincms_extra_context', {}):
                return template_name, context

            return render(request, template_name, context)
        except ValueError:
            return response
    return _decorator


def redirect(view_name, *args, **kwargs):
    try:
        url = app_reverse(view_name, 'zipfelchappe.urls', *args, **kwargs)
        return _redirect(url)
    except NoReverseMatch:
        return _redirect(view_name, *args, **kwargs)


#-----------------------------------
# views
#-----------------------------------

class ProjectListView(FeincmsRenderMixin, ListView):

    context_object_name = "project_list"
    model = Project

    def get_queryset(self):
        return Project.objects.online().select_related('backers')

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        if hasattr(Project, 'categories'):
            context['category_list'] = Category.objects.all()
        return context


class ProjectCategoryListView(FeincmsRenderMixin, ListView):
    context_object_name = "project_list"
    model = Project

    def get_queryset(self):
        if not hasattr(Project, 'categories'):
            raise Http404

        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        online_projects = Project.objects.online().select_related(depth=2)
        return online_projects.filter(categories=category)

    def get_context_data(self, **kwargs):
        context = super(ProjectCategoryListView, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        return context


class ProjectDetailView(FeincmsRenderMixin, DetailView):

    context_object_name = "project"
    model = Project

    def get_queryset(self):
        return Project.objects.online().select_related('backers', 'pledges')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = self.prepare()
        if response:
            return response

        response = self.render_to_response(self.get_context_data(object=self.object))
        return self.finalize(response)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        context['disqus_shortname'] = app_settings.DISQUS_SHORTNAME
        context['updates'] = self.get_object().updates.filter(
            status=Update.STATUS_PUBLISHED
        )

        context['thank_you'] = 'thank_you' in self.request.GET
        pledge_id = self.request.GET.get('pledge', -1)
        context['pledge'] = get_object_or_none(Pledge, pk=pledge_id)

        return context

    def prepare(self):
        """
        Prepare / pre-process content types. If this method returns anything,
        it is treated as a ``HttpResponse`` and handed back to the visitor.
        """

        http404 = None      # store eventual Http404 exceptions for re-raising,
                            # if no content type wants to handle the request
        successful = False  # did any content type successfully end processing?

        contents = tuple(self.object._feincms_content_types_with_process)
        for content in self.object.content.all_of_type(contents):
            try:
                r = content.process(self.request, view=self)
                if r in (True, False):
                    successful = r
                elif r:
                    return r
            except Http404, e:
                http404 = e

        if not successful:
            if http404:
                # re-raise stored Http404 exception
                raise http404

    def finalize(self, response):
        """
        Runs finalize() on content types having such a method, adds headers and
        returns the final response.
        """

        if not isinstance(response, HttpResponse):
            # For example in the case of inheritance 2.0
            return response

        contents = tuple(self.object._feincms_content_types_with_finalize)
        for content in self.object.content.all_of_type(contents):
            r = content.finalize(self.request, response)
            if r:
                return r

        return response


class UpdateDetailView(FeincmsRenderMixin, DetailView):

    context_object_name = 'update'
    model = Update

    def get_context_data(self, **kwargs):
        context = super(UpdateDetailView, self).get_context_data(**kwargs)
        context['project'] = self.get_object().project
        return context


@feincms_render
def project_back_form(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if not project.is_active:
        messages.info(request, _('This project has ended and does not accept'
                                 ' pledges anymore.'))
        return redirect('zipfelchappe_project_detail',
                        kwargs={'slug': project.slug})

    form_kwargs = {
        'project': project,
    }

    session_pledge = get_session_pledge(request)
    if session_pledge and session_pledge.project == project:
        form_kwargs.update({
            'instance': session_pledge,
        })

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


@feincms_render
@requires_pledge
def backer_authenticate(request, pledge):
    BackerModel = get_backer_model()

    if pledge.backer is not None:
        return redirect('zipfelchappe_payment')

    if request.user.is_authenticated():
        try:
            backer = BackerModel.objects.get(user=request.user)
            pledge.backer = backer
            pledge.save()
            return redirect('zipfelchappe_payment')
        except BackerModel.DoesNotExist:
            if use_default_backer_model():
                pledge.backer = BackerModel.objects.create(user=request.user)
                pledge.save()
                return redirect('zipfelchappe_payment')
            else:
                return redirect('zipfelchappe_backer_profile')
    else:
        return ('zipfelchappe/backer_authenticate_form.html', {
            'pledge': pledge,
            'project': pledge.project,
            'login_form': AuthenticationForm(),
            'register_user_form': forms.RegisterUserForm(),
            'register_backer_form': forms.RegisterBackerForm(),
            'userless_form': forms.UserlessBackerForm()
        })


@requires_pledge_cbv
class BackerProfileView(FeincmsRenderMixin, PledgeContextMixin, FormView):
    form_class = forms.AuthenticatedBackerForm
    template_name = "zipfelchappe/backer_profile_form.html"

    def get_success_url(self):
        return app_reverse('zipfelchappe_backer_authenticate',
                           'zipfelchappe.urls')

    def form_valid(self, form):
        backer = form.save(commit=False)
        backer.user = self.request.user
        backer.save()
        return super(BackerProfileView, self).form_valid(form)


@requires_pledge_cbv
class BackerLoginView(FeincmsRenderMixin, PledgeContextMixin, FormView):
    form_class = AuthenticationForm
    permanent = False
    template_name = "zipfelchappe/backer_login_form.html"

    def get_success_url(self):
        return app_reverse('zipfelchappe_backer_authenticate',
                           'zipfelchappe.urls')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(BackerLoginView, self).form_valid(form)


@feincms_render
@requires_pledge
def backer_register(request, pledge):

    if request.method == 'POST':
        register_user_form = forms.RegisterUserForm(request.POST)
        register_backer_form = forms.RegisterBackerForm(request.POST)

        if register_user_form.is_valid() and register_backer_form.is_valid():
            user = register_user_form.save()
            password = register_user_form.cleaned_data['password1']
            user = authenticate(username=user.username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                backer = register_backer_form.save(commit=False)
                backer.user = user
                backer.save()
                return redirect('zipfelchappe_backer_authenticate')
            else:
                # This should not be possible. Hower, always be prepared:
                messages.error(request, _(
                    'Unfortuantley you could not be'
                    'logged in after registration. Please try again!'
                ))
                return redirect('zipfelchappe_project_list')
    else:
        register_user_form = forms.RegisterUserForm()
        register_backer_form = forms.RegisterBackerForm()

    return ('zipfelchappe/backer_register_form.html', {
        'pledge': pledge,
        'project': pledge.project,
        'register_user_form': register_user_form,
        'register_backer_form': register_backer_form,
    })


@requires_pledge_cbv
class UserlessBackerView(FeincmsRenderMixin, PledgeContextMixin, FormView):
    form_class = forms.UserlessBackerForm
    template_name = "zipfelchappe/backer_userless_form.html"

    def get_success_url(self):
        return reverse('zipfelchappe_payment')

    def form_valid(self, form):
        backer = form.save()
        self.pledge.backer = backer
        self.pledge.save()
        return super(UserlessBackerView, self).form_valid(form)


def pledge_thankyou(request):
    pledge = get_session_pledge(request)

    if not pledge:
        return redirect('zipfelchappe_project_list')
    else:
        mail_template = get_object_or_none(MailTemplate,
            project=pledge.project, action=MailTemplate.ACTION_THANKYOU)
        send_pledge_completed_message(pledge, mail_template)
        del request.session['pledge_id']
        url = app_reverse('zipfelchappe_project_detail', 'zipfelchappe.urls',
                          kwargs={'slug': pledge.project.slug})
        return redirect(url + '?thank_you&pledge=%d' % pledge.pk)


def pledge_cancel(request):
    pledge = get_session_pledge(request)

    if not pledge:
        return redirect('zipfelchappe_project_list')
    else:
        messages.info(request, _('Your pledge was canceled'))
        return redirect('zipfelchappe_project_detail', kwargs={
            'slug': pledge.project.slug
        })


class PledgeLostView(FeincmsRenderMixin, TemplateView):
    template_name = "zipfelchappe/pledge_lost.html"


@csrf_exempt
@staff_member_required
def send_test_mail(request):
    """ Used from the admin to test mail templates """
    project = get_object_or_404(Project, pk=request.POST.get('project', -1))

    action = request.POST.get('action', None)
    subject = request.POST.get('subject', None)
    template = request.POST.get('template', None)
    recipient = request.POST.get('recipient', None)

    BackerModel = get_backer_model()

    mail_template = MailTemplate(
        project=project,
        action=action,
        subject=subject,
        template=template
    )

    fake_plede = Pledge(
        project=project,
        amount=10,
        backer=BackerModel(
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
