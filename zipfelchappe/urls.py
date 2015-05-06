from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^$',
        views.ProjectListView.as_view(),
        name='zipfelchappe_project_list'),
    url(r'^project/(?P<slug>[\w-]+)/$',
        views.ProjectDetailView.as_view(),
        name='zipfelchappe_project_detail'),
    url(r'^project/(?P<slug>[\w-]+)/backed/$',
        views.ProjectDetailHasBackedView.as_view(),
        name='zipfelchappe_project_backed'),
    url(r'^category/(?P<slug>[\w-]+)/',
        views.ProjectCategoryListView.as_view(),
        name='zipfelchappe_project_category_list'),
    url(r'^back/(?P<slug>[\w-]+)/$',
        views.backer_create_view,
        name='zipfelchappe_backer_create'),
    url(r'^backer/authenticate/$',
        views.backer_authenticate,
        name='zipfelchappe_backer_authenticate'),
    url(r'^pledge/thankyou/$',
        views.pledge_thankyou,
        name='zipfelchappe_pledge_thankyou'),
    url(r'^pledge/cancel/$',
        views.pledge_cancel,
        name='zipfelchappe_pledge_cancel'),
    url(r'^pledge/lost/$',
        views.PledgeLostView.as_view(),
        name='zipfelchappe_pledge_lost'),
)
