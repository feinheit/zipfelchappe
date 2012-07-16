from django.conf.urls import patterns, url
from django.contrib import admin
from django.db import models
from django.views.generic import ListView
from django.utils.translation import ugettext_lazy as _

from ..base import CreateUpdateModel
from ..models import Project
from ..urls import urlpatterns, views

class Category(CreateUpdateModel):
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True)
    ordering = models.SmallIntegerField(_('ordering'), default=0)

    class Meta:
        app_label = 'zipfelchappe'
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['ordering']

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('zipfelchappe_project_category_list', (self.slug,))

    @property
    def project_count(self):
        return self.projects.count()


class ProjectCategoryListView(ListView):
    context_object_name = "project_list"
    queryset = Project.objects.online().select_related()
    model = Project

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Project.objects.filter(categories=category)

    def get_context_data(self, **kwargs):
        context = super(ProjectCategoryListView, self).get_context_data(**kwargs)
        context['categoriy_list'] = Category.objects.filter(
            projects__in=self.queryset
        )
        return context


urlpatterns += patterns(
    url(r'^category/(?P<slug>[\w-]+)/',
        ProjectCategoryListView.as_view(),
        name='zipfelchappe_project_category_list'),
)


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['title', 'slug']
    prepopulated_fields = {
        'slug': ('title',),
    }

admin.site.register(Category, CategoryAdmin)


def register(cls, admin_cls):
    cls.add_to_class('categories', models.ManyToManyField(Category,
        verbose_name=_('categories'), related_name='projects',
        null=True, blank=True)
    )

    admin_cls.fieldsets.insert(2, [
        _('categories'), {
            'fields': ['categories'],
            'classes': ['feincms_inline'],
        }
    ])

    admin_cls.filter_horizontal += ('categories',)
