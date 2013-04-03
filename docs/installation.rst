.. _installation:


Installation
============

Zipfelchappe requires at least:

* `Django v1.4 <https://github.com/django/django>`_
* `FeinCMS v1.7 <https://github.com/feincms/feincms>`_
* `requests v1.0 <https://github.com/kennethreitz/requests/>`_

To install them via pip, just do::

    pip install django feincms requests


It's highly recommendable to install zipfelchappe via pip::

    pip install zipfelchappe

Add zipfelchappe to your INSTALLED_APPS. Notice that feincms is required too::

    INSTALLED_APPS = (
        ...
        'feincms',

        'zipfelchappe',
        'zipfelchappe.paypal',
        'zipfelchappe.postfinace',
    )

If you need support for multiple languages in your projects, add
``zipfelchappe.translations`` to INSTALLED_APPS.


Payment modules also that you include their urls to your root urls::

    urlpatterns += patterns('',
        url(r'^paypal/', include('zipfelchappe.paypal.urls')),
        url(r'^postfinance/', include('zipfelchappe.postfinance.urls')),
    )

Now, add zipfelchappe to your feincms application content modules. This is
usually done in your projects ``models.py`` file::

    Page.create_content_type(ApplicationContent, APPLICATIONS=(
        ('zipfelchappe.urls', _('Zipfelchappe projects')),
    ))

The next step is to define the content types you want use:: :

    Project.create_content_type(RichTextContent)
    Project.create_content_type(MediaFileContent)

Content types are FeinCMS building blocks, that allow you to use any kind of
content in your projects. Usually the two mentioned above offer quite everything
you need, but in case you want to do something more, checkout
`feincms.org <http://feincms.org>`_.


The last set is to configure zipfelchappe according to your needs. Here is
a full example with all available configuration options, you can tailor them
to suit your needs:
::
    # Payment providers. Read more about this in the seperate chapter
    ZIPFELCHAPPE_PAYMENT_PROVIDERS = (
        ('paypal', 'Paypal'),
        ('postfinance', 'Postfinance'),
    )

    # The currencies you can choose for projects (only 1 per project)
    ZIPFELCHAPPE_CURRENCIES = ('CHF', 'EUR', 'USD')

    # Will try to use django comments if set to None
    ZIPFELCHAPPE_DISQUS_SHORTNAME = None

    # Number of projects per page in project list
    ZIPFELCHAPPE_PAGINATE_BY = 10

    # Offers a flag if someone does not wish to appear on the backer list
    ZIPFELCHAPPE_ALLOW_ANONYMOUS_PLEDGES = True

    # Paypal provider settings
    ZIPFELCHAPPE_PAYPAL = {
        'USERID': '',
        'PASSWORD': '',
        'SIGNATURE': '',
        'APPLICATIONID': '', # not required for testing
        'LIVE': False,
        'RECEIVERS': [{
            'email': 'whogetsthemoney@mommy.com',
            'percent': 100,
        }]
    }

    # Postfinance provider settings
    ZIPFELCHAPPE_POSTFINANCE = {
        'PSPID': '',
        'LIVE': False,
        'SHA1_IN': '',
        'SHA1_OUT': '',
        'USERID': '', # This is the Postfinance Direct Link API user
        'PSWD': '',   # and his password
    }
