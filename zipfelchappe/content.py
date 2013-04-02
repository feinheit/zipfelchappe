from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from .models import Project


class ProjectTeaserContent(models.Model):
    """ Shows one project with a link to the project detail page """

    project = models.ForeignKey(Project, verbose_name=_('project'),
        related_name='teasercontents')

    class Meta:
        verbose_name = _('project teaser')
        verbose_name_plural = _('project teasers')
        abstract = True

    def render(self, request, *args, **kwargs):
        return render_to_string('zipfelchappe/project_teaser.html', {
            'content': self,
            'ct': True,
            'project': self.project,
        })


class ProjectTeaserRowContent(models.Model):
    """ A row of three project teasers with links to each project """

    project1 = models.ForeignKey(Project, verbose_name=_('project 1'),
        related_name='teaserrowcontents1', blank=True, null=True)

    project2 = models.ForeignKey(Project, verbose_name=_('project 2'),
        related_name='teaserrowcontents2', blank=True, null=True)

    project3 = models.ForeignKey(Project, verbose_name=_('project 3'),
        related_name='teaserrowcontents3', blank=True, null=True)

    class Meta:
        verbose_name = _('project teaser row')
        verbose_name_plural = _('project teaser row')
        abstract = True

    def render(self, request, *args, **kwargs):
        return render_to_string('zipfelchappe/project_teaser_row.html', {
            'content': self,
            'project_list': (self.project1, self.project2, self.project3)
        })
