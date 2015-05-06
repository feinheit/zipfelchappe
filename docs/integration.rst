.. _integration:

Integration
===========

Project
-------
Register the available regions in your models.py::

    from zipfelchappe.models import Project

    Project.register_regions(
        ('main', _('Content')),
        ('thankyou', _('Thank you')),
    )


Add the content types like in FeinCMS::

    Project.create_content_type(RichTextContent)
    Project.create_content_type(
        MediaFileContent,
        TYPE_CHOICES=(
            ('default', _('default')),
        ))

Templates
---------

To integrate zipfelchappe into your page, it's often advisable to override
the base template ``zipfelchappe/base.html``. When you do this, take care to
support the three required blocks for zipfelchappe:

 * maincontent
 * sidebar
 * javascript


You also need to have the feincms_page object in your template context even for the payment views
which don't use the application content. Either that or make sure the payment templates don't inherit
from your common feincms base template.

The simplest way to add the feincms_page object to the template context is to add the context processor::

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        "feincms.context_processors.add_page_if_missing",
    )


Migrations
----------

Zipfelchappe does not come with any sort of migrations itself. This would be
a bad idea anyway because of it's highly configurable nature. Howerver, there
is no reason why you shouldn't use South or whatever you like in your project.

If you are using South, you will have to define a custom migration path for
zipfelchappe. Something like::

    SOUTH_MIGRATION_MODULES = {
        'zipfelchappe': 'yourproject.migrate.zipfelchappe',
    }


Extensions
-----------

If you need to add some custom fields to your projects, you can leverage the
FeinCMS extension mechanism. Take a look at some of the built-in exenstion
and read the documentation at `feincms.org <http://feincms.org>`_.

Zipfelchappe provides a ``categories`` extension.


BackerProfile
-------------

To be added.
