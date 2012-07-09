from functools import wraps

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse_lazy

from . import forms
from .models import Project, Category, Pledge
from .utils import get_backer_model, get_object_or_none

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
            redirect('zipfelchappe_project_list')
    return _decorator


class PledgeContextMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(PledgeContextMixin, self).get_context_data(*args, **kwargs)
        pledge = get_session_pledge(self.request)
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

    if request.user.is_authenticated():
        try:
            backer = BackerModel.objects.get(user=request.user)
            return redirect('zipfelchappe_paynow')
        except BackerModel.DoesNotExist:
            return redirect('zipfelchappe_backer_profile')
    else:
        login_form = AuthenticationForm()
        register_user_form = forms.RegisterUserForm()
        register_backer_form = forms.RegisterBackerForm()
        anonymous_form = forms.AnonymousBackerForm()

        return render(request, 'zipfelchappe/backer_authenticate_form.html', {
            'pledge': pledge,
            'project': pledge.project,
            'login_form': login_form,
            'register_user_form': register_user_form,
            'register_backer_form': register_backer_form,
            'anonymous_form': anonymous_form
        })


class BackerLoginView(PledgeContextMixin, FormView):
    form_class = AuthenticationForm
    template_name = "zipfelchappe/backer_login_form.html"
    success_url = reverse_lazy('zipfelchappe_backer_authenticate')


class BackerProfileView(PledgeContextMixin, FormView):
    form_class = forms.AuthenticatedBackerForm
    template_name = "zipfelchappe/backer_profile_form.html"
    success_url = reverse_lazy('zipfelchappe_backer_authenticate')

    def get_initial(self, *args, **kwargs):
        initial = super(BackerProfileView, self).get_initial(*args, **kwargs)
        initial.update({ 'user': request.user })
        return initial


@requires_pledge
def paynow(request, pledge):
    del request.session['pledge_id']
    return HttpResponse('pay now: %s!' % pledge)
