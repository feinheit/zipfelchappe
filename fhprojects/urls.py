from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.shortcuts import redirect
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^payment/$', lambda r: redirect('zipfelchappe_paypal_payment'),
        name='zipfelchappe_payment'),
    url(r'^paypal/', include('zipfelchappe.paypal.urls')),
    url(r'^newsletter/',
        include('yesimeanit.showoff.newsletter_subscriptions.urls')),
    url(r'', include('feincms.urls')),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        url(r'^uploads/(.*)', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': True,
            }),
    )
