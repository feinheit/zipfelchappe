
=========================
zipfelchappe crowdfunding
=========================

Zipfelchappe is an open source crowdfunding platform based on the django framework.
Inspired by various crowdfunding pages like `kickstarter.com <http://kickstarter.com>`_,
`fundable.com <http://fundable.com>`_, `indiegogo.com <http://indiegogo.com>`_
and `wemakeit.ch <http://wemakeit.ch>`_, we try to offer the very same
functionality and a little bit more.

The main advantage of zipfelchappe: it's free, customizable, styleable and can
be integrated in your existing webpage. Free means not only that you are allowed
to install and use the software freely, you also decide where the money goes!
Zipfelchappe does not cut a share of your pledges or raise a monthly fee.

See http://projects.feinheit.ch for an example page running zipfelchappe.

.. toctree::
   :maxdepth: 1


.. _installation:


Installation
============

Zipfelchappe requires at least:

* `Django v1.4 <https://github.com/django/django>`_
* `FeinCMS v1.5 <https://github.com/feincms/feincms>`_
* `requests <https://github.com/kennethreitz/requests/>`_

To install them via pip, just do::

    pip install django feincms requests

To install zipfelchappe, either checkout out the
`git repository <https://github.com/feinheit/zipfelchappe>`_ or install it
with pip::

    pip install zipfelchappe

Add zipfelchappe to your INSTALLED_APPS. Notice that feincms is required too::

    INSTALLED_APPS = (
        ...
        'feincms',

        'zipfelchappe',
        'zipfelchappe.paypal',
    )

If you need support for multiple languages in your projects, add
``zipfelchappe.translations`` to INSTALLED_APPS.

You need to register a payment module in order to receive pledges. To use the
default paypal implementation, just add this to your project urls::

    urlpatterns += patterns('',
        url(r'^zipfelchappe/paypal/', include('zipfelchappe.paypal.urls')),
    )

Now, add zipfelchappe to your feincms application content modules. This is
usually done in your projects ``models.py`` file::

    Page.create_content_type(ApplicationContent, APPLICATIONS=(
        ('zipfelchappe.urls', _('Zipfelchappe projects')),
    ))

Configure the extensions and content types for your project:

    Project.register_extensions(
        'zipfelchappe.extensions.categories',
        'zipfelchappe.extensions.paypal_receivers',
    )

    Project.create_content_type(RichTextContent)
    Project.create_content_type(MediaFileContent)

Finally, add the following settings to your ``settings.py`` file::

    ZIPFELCHAPPE_PAYPAL_USERID = ''
    ZIPFELCHAPPE_PAYPAL_PASSWORD = ''
    ZIPFELCHAPPE_PAYPAL_SIGNATURE = ''
    ZIPFELCHAPPE_PAYPAL_LIVE = False

    ZIPFELCHAPPE_DISQUS_SHORTNAME = ''


.. _integration:

Integration
===========


Funding framework
-----------------

Right now, zipfelchappe supports the commonly known "all or nothing" goal based
funding principle. This means:

 * You set a goal when you start your project
 * People may back your project in a limited period of time
 * After this period, money will only be collected if your goal was reached

To implement this behaviour, we use `Paypal's Preapproved Adaptive Payments`_.
However, you are free to use any other funding framework or payment system you
can think of. We will try to collect these methods and implementations so you
can choose which way works best for you.

.. _Paypal's Preapproved Adaptive Payments: https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_api_APIntro


TODO: Describe what is necessary to implement a custom framework


Templates
---------

To integrate zipfelchappe into your page, it's often advisable to override
the base template ``zipfelchappe/base.html``. When you do this, take care to
support the three required block of zipfelchappe:

 * maincontent
 * sidebar
 * javascript


Custom backer model
-------------------

Zipfelchappe comes with a very basic backer model. However, you can define a
custom backer model to collect exactly the data need to gather from your backers.

To do so, define a Model which derives from ``zipfelchappe.models.BaseBacker``::

    from zipfelchappe.models import BackerBase

    class ExtendedBacker(BackerBase):
        address = models.CharField(_('address'), max_length=100)
        city = models.CharField(_('city'), max_length=100)
        state = models.CharField(_('state'), max_length=100)

        ...

And set you backer model in your settings::

    ZIPFELCHAPPE_BACKER_MODEL = 'mybackers.ExtendedBacker'
