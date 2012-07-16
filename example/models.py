from django.utils.translation import ugettext_lazy as _

from feincms.module.page.models import Page
from feincms.content.richtext.models import RichTextContent
from feincms.content.medialibrary.v2 import MediaFileContent

from zipfelchappe.models import Project

from zipfelchappe.extensions import paypal_receivers

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

Page.create_content_type(RichTextContent)
Page.create_content_type(MediaFileContent, TYPE_CHOICES=MEDIA_TYPE_CHOICES)

Page.register_extensions('symlinks')

Project.register_regions(
    ('main', _('Content')),
)

Project.register_extensions(paypal_receivers)

Project.create_content_type(RichTextContent, cleanse=False, regions=('main',))
Project.create_content_type(MediaFileContent, TYPE_CHOICES=MEDIA_TYPE_CHOICES)
