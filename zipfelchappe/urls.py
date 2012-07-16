from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from . import views
from .extensions.categories import ProjectCategoryListView

urlpatterns = patterns('',
    url(r'^$',
        views.ProjectListView.as_view(),
        name='zipfelchappe_project_list'),
    url(r'^project/(?P<slug>[\w-]+)/$',
        views.ProjectDetailView.as_view(),
        name='zipfelchappe_project_detail'),
    url(r'^category/(?P<slug>[\w-]+)/',
        ProjectCategoryListView.as_view(),
        name='zipfelchappe_project_category_list'),
    url(r'^back/(?P<slug>[\w-]+)/$',
        views.project_back_form,
        name='zipfelchappe_project_back_form'),
    url(r'^backer/authenticate/$',
        views.backer_authenticate,
        name='zipfelchappe_backer_authenticate'),
    url(r'^backer/profile/$',
        views.BackerProfileView.as_view(),
        name='zipfelchappe_backer_profile'),
    url(r'^backer/login/$',
        views.BackerLoginView.as_view(),
        name='zipfelchappe_backer_login'),
    url(r'^backer/register/$',
        views.backer_register,
        name='zipfelchappe_backer_register'),
    url(r'^backer/userless/$',
        views.UserlessBackerView.as_view(),
        name='zipfelchappe_backer_userless'),
    url(r'^pledge/lost/$',
        views.PledgeLostView.as_view(),
        name='zipfelchappe_pledge_lost'),
)
