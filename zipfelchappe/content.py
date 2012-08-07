from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from .models import Project

class ProjectTeaserContent(models.Model):

    project = models.ForeignKey(Project, verbose_name=_('project'),
        related_name='teasercontents')

    class Meta:
        verbose_name = _('project teaser')
        verbose_name_plural = _('project teasers')
        abstract = True

    def render(self, request, *args, **kwargs):
        return render_to_string('zipfelchappe/project_teaser.html', {
            'ct': True,
            'project': self.project,
        })
