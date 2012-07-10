from functools import wraps

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from . import forms
from .models import Project, Category, Pledge
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

#-----------------------------------
# views
#-----------------------------------

class ProjectListView(ListView):

    context_object_name = "project_list"
    queryset = Project.objects.online().select_related()
    model = Project

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        context['categoriy_list'] = Category.objects.filter(
            projects__in=self.queryset
        )
        return context


class ProjectCategoryListView(ListView):

    context_object_name = "project_list"
    queryset = Project.objects.online().select_related()
    model = Project

    def get_context_data(self, **kwargs):
        context = super(ProjectCategoryListView, self).get_context_data(**kwargs)
        context['categoriy_list'] = Category.objects.filter(
            projects__in=self.queryset
        )
        return context

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Project.objects.filter(categories=category)

class ProjectDetailView(DetailView):

    context_object_name = "project"
    queryset = Project.objects.online().select_related()
    model = Project

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = self.prepare()
        if response:
            return response

        response = self.render_to_response(self.get_context_data(object=self.object))
        return self.finalize(response)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def prepare(self):
        """
        Prepare / pre-process content types. If this method returns anything,
        it is treated as a ``HttpResponse`` and handed back to the visitor.
        """

        http404 = None     # store eventual Http404 exceptions for re-raising,
                           # if no content type wants to handle the current self.request
        successful = False # did any content type successfully end processing?

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


def project_back_form(request, slug):
    project = get_object_or_404(Project, slug=slug)
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

    return render(request, 'zipfelchappe/project_back_form.html', {
        'project': project,
        'form': form,
    })


@requires_pledge
def backer_authenticate(request, pledge):
    BackerModel = get_backer_model()

    if pledge.backer is not None:
        return redirect('zipfelchappe_paynow')

    if request.user.is_authenticated():
        try:
            backer = BackerModel.objects.get(user=request.user)
            pledge.backer = backer
            pledge.save()
            return redirect('zipfelchappe_paynow')
        except BackerModel.DoesNotExist:
            if use_default_backer_model():
                pledge.backer = BackerModel.objects.create(user=request.user)
                pledge.save()
                return redirect('zipfelchappe_paynow')
            else:
                return redirect('zipfelchappe_backer_profile')
    else:
        return render(request, 'zipfelchappe/backer_authenticate_form.html', {
            'pledge': pledge,
            'project': pledge.project,
            'login_form': AuthenticationForm(),
            'register_user_form': forms.RegisterUserForm(),
            'register_backer_form': forms.RegisterBackerForm(),
            'userless_form': forms.UserlessBackerForm()
        })


@requires_pledge_cbv
class BackerProfileView(PledgeContextMixin, FormView):
    form_class = forms.AuthenticatedBackerForm
    template_name = "zipfelchappe/backer_profile_form.html"
    success_url = reverse_lazy('zipfelchappe_backer_authenticate')

    def form_valid(self, form):
        backer = form.save(commit=False)
        backer.user = self.request.user
        backer.save()
        return super(BackerProfileView, self).form_valid(form)


@requires_pledge_cbv
class BackerLoginView(PledgeContextMixin, FormView):
    form_class = AuthenticationForm
    template_name = "zipfelchappe/backer_login_form.html"
    success_url = reverse_lazy('zipfelchappe_backer_authenticate')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(BackerLoginView, self).form_valid(form)


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
                messages.error(request, _('Unfortuantley you could not be'
                    'logged in after registration. Please try again!'))
                return redirect('zipfelchappe_project_list')
    else:
        register_user_form = forms.RegisterUserForm()
        register_backer_form = forms.RegisterBackerForm()

    return render(request, 'zipfelchappe/backer_register_form.html', {
        'pledge': pledge,
        'project': pledge.project,
        'register_user_form': register_user_form,
        'register_backer_form': register_backer_form,
    })


@requires_pledge_cbv
class UserlessBackerView(PledgeContextMixin, FormView):
    form_class = forms.UserlessBackerForm
    template_name = "zipfelchappe/backer_userless_form.html"
    success_url = reverse_lazy('zipfelchappe_paynow')

    def form_valid(self, form):
        backer = form.save()
        self.pledge.backer = backer
        self.pledge.save()
        return super(UserlessBackerView, self).form_valid(form)


@requires_pledge
def paynow(request, pledge):
    del request.session['pledge_id']
    return HttpResponse('pay now: %s!' % pledge)

class PledgeLostView(TemplateView):
    template_name = "zipfelchappe/pledge_lost.html"
