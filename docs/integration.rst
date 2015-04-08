.. _integration:

Integration
===========


Templates
---------

To integrate zipfelchappe into your page, it's often advisable to override
the base template ``zipfelchappe/base.html``. When you do this, take care to
support the three required blocks for zipfelchappe:

 * maincontent
 * sidebar
 * javascript


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
