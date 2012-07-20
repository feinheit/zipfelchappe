from django.utils.translation import ugettext_lazy as _

from feincms.module.page.models import Page
from feincms.content.richtext.models import RichTextContent
from feincms.content.medialibrary.v2 import MediaFileContent
from feincms.content.application.models import ApplicationContent
from feincms.content.raw.models import RawContent

from zipfelchappe.models import Project
from zipfelchappe.content import ProjectTeaserContent

MEDIA_TYPE_CHOICES = (
    ('full', _('full')),
    ('left', _('left')),
    ('right', _('right')),
)

Page.register_templates({
    'title': 'Standard template',
    'path': 'feincms_base.html',
    'regions': (
        ('main', _('Main content area')),
        ),
    }, {
    'title': 'With moodboard',
    'path': 'feincms_moodboard.html',
    'regions': (
        ('main', _('Main content area')),
        ('moodboard', _('Moodboard'), 'inherited'),
        ),
    })

Page.register_extensions(
    'feincms.module.page.extensions.titles',
    'feincms.module.page.extensions.navigation',
    'feincms.module.extensions.seo',
    'feincms.module.extensions.changedate',
    'feincms.module.extensions.ct_tracker',
    )

Page.create_content_type(ApplicationContent, APPLICATIONS=(
    ('zipfelchappe.urls', _('Zipfelchappe projects')),
))

Page.create_content_type(RichTextContent)
Page.create_content_type(MediaFileContent, TYPE_CHOICES=MEDIA_TYPE_CHOICES)
Page.create_content_type(ProjectTeaserContent)
Page.create_content_type(RawContent)


Project.register_regions(
    ('main', _('Content')),
    ('updates', _('Updates')),
)

Project.register_extensions(
    #'zipfelchappe.extensions.categories',
    'zipfelchappe.extensions.paypal_receivers',
)

Project.create_content_type(RichTextContent)
Project.create_content_type(MediaFileContent, TYPE_CHOICES=MEDIA_TYPE_CHOICES)
