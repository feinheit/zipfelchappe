from django.utils.translation import ugettext_lazy as _

from feincms.module.page.models import Page
from feincms.content.richtext.models import RichTextContent
from feincms.content.medialibrary.v2 import MediaFileContent
from feincms.content.application.models import ApplicationContent

from zipfelchappe.models import Project

MEDIA_TYPE_CHOICES = (
    ('full', _('full')),
    ('left', _('left')),
    ('right', _('right')),
)

Page.register_templates({
    'title': _('Standard'),
    'path': 'base.html',
    'regions': (
        ('main', _('Content')),
    ),
})


Page.register_extensions('symlinks')

Page.create_content_type(ApplicationContent, APPLICATIONS=(
    ('zipfelchappe.urls', _('Zipfelchappe projects')),
))

Page.create_content_type(RichTextContent)
Page.create_content_type(MediaFileContent, TYPE_CHOICES=MEDIA_TYPE_CHOICES)


Project.register_regions(
    ('main', _('Content')),
)

Project.register_extensions(
    'zipfelchappe.extensions.categories',
    'zipfelchappe.extensions.paypal_receivers',
)

Project.create_content_type(RichTextContent)
Project.create_content_type(MediaFileContent, TYPE_CHOICES=MEDIA_TYPE_CHOICES)
