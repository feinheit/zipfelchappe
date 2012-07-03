from django.utils.translation import ugettext_lazy as _

from feincms.content.richtext.models import RichTextContent
from feincms.content.medialibrary.v2 import MediaFileContent

from zipfelchappe.projects.models import Project

# TODO: This should be removed once the project is converted to a library

Project.register_regions(
    ('main', _('Content')),
)

Project.create_content_type(RichTextContent, cleanse=False, regions=('main',))
Project.create_content_type(MediaFileContent, TYPE_CHOICES=(
    ('default', _('default')),
))
