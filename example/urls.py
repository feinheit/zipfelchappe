from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^account/', include('django.contrib.auth.urls')),
    url(r'^$', RedirectView.as_view(url='/projects/')),
    url(r'^paypal/', include('zipfelchappe.paypal.urls')),
    url(r'^postfinance/', include('zipfelchappe.postfinance.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
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
