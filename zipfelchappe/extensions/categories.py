from django.contrib import admin
from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.utils.translation import ugettext_lazy as _

from ..base import CreateUpdateModel
from ..models import Project

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
        if not hasattr(Project, 'categories'):
            raise Http404

        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Project.objects.filter(categories=category)

    def get_context_data(self, **kwargs):
        context = super(ProjectCategoryListView, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.filter(
            projects__in=self.queryset
        )
        return context


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['title', 'slug']
    prepopulated_fields = {
        'slug': ('title',),
    }


def register(cls, admin_cls):
    admin.site.register(Category, CategoryAdmin)

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
