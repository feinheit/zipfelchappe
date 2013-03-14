
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from feincms.models import Base


class ProjectTranslation(Base):

    translation_of = models.ForeignKey('zipfelchappe.Project',
        related_name='translations')

    lang = models.CharField(_('language'), max_length=10,
        choices=settings.LANGUAGES)

    title = models.CharField(_('title'), max_length=100)

    teaser_text = models.TextField(_('teaser text'), blank=True)

    class Meta:
        app_label = 'zipfelchappe'
        verbose_name = _('translation')
        verbose_name_plural = _('translations')
        unique_together = (('translation_of', 'lang'),)

    def __unicode__(self):
        try:
            return u'%s (%s)' % (self.translation_of, self.get_lang_display())
        except:
            return 'New project translation'


class RewardTranslation(models.Model):

    translation = models.ForeignKey(ProjectTranslation, related_name='rewards')

    translation_of = models.ForeignKey('zipfelchappe.Reward',
        related_name='translations')

    description = models.TextField(_('description'), blank=True)

    class Meta:
        app_label = 'zipfelchappe'
        verbose_name = _('reward')
        verbose_name_plural = _('rewards')
        unique_together = (('translation', 'translation_of'))

    def __unicode__(self):
        return u'%s (%s)' % (self.translation_of,
            self.translation.get_lang_display())


class UpdateTranslation(models.Model):

    translation = models.ForeignKey(ProjectTranslation, related_name='updates')

    translation_of = models.ForeignKey('zipfelchappe.Update',
        related_name='translations')

    title = models.CharField(_('title'), max_length=100)

    content = models.TextField(_('content'), blank=True)

    # TODO: Maybe image, external and attachment should be translateable too

    class Meta:
        app_label = 'zipfelchappe'
        verbose_name = _('updates')
        verbose_name_plural = _('updates')
        unique_together = (('translation', 'translation_of'))

    def __unicode__(self):
        return u'%s (%s)' % (self.translation_of,
            self.translation.get_lang_display())


class MailTemplateTranslation(models.Model):

    translation = models.ForeignKey(ProjectTranslation,
        related_name='mail_template')

    translation_of = models.ForeignKey('zipfelchappe.MailTemplate',
        related_name='translations')

    subject = models.CharField(_('subject'), max_length=200)

    template = models.TextField(_('template'))

    class Meta:
        app_label = 'zipfelchappe'
        verbose_name = _('mail')
        verbose_name_plural = _('mails')
        unique_together = (('translation', 'translation_of'))

    def __unicode__(self):
        return u'%s (%s)' % (self.translation_of,
            self.translation.get_lang_display())
