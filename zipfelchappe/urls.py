from django.conf.urls.defaults import *

from . import views

urlpatterns = patterns('',
    url(r'^projects/$',
        views.ProjectListView.as_view(),
        name='zipfelchappe_project_list'),
    url(r'^projects/category/(?P<slug>[\w-]+)/',
        views.ProjectCategoryListView.as_view(),
        name='zipfelchappe_project_category_list'),
    url(r'^projects/(?P<slug>[\w-]+)/$',
        views.ProjectDetailView.as_view(),
        name='zipfelchappe_project_detail'),
)
