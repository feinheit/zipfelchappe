from django.utils.translation import ugettext_lazy as _

from feincms.content.richtext.models import RichTextContent
from feincms.content.medialibrary.v2 import MediaFileContent

from zipfelchappe.models import Project

DIMENSION_CHOICES = (
    ('large', _('Large (960x540)')),
    ('medium', _('Medium (640x360)')),
    ('small', _('Small (480x270)')),
)

MEDIA_TYPE_CHOICES = (
    ('full', _('full')),
    ('left', _('left')),
    ('right', _('right')),
)

Project.register_regions(
    ('main', _('Content')),
)

Project.create_content_type(RichTextContent, cleanse=False, regions=('main',))
Project.create_content_type(MediaFileContent, TYPE_CHOICES=MEDIA_TYPE_CHOICES)
