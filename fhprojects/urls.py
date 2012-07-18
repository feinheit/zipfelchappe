from django.contrib import admin
from django.conf.urls import patterns, include, url

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^newsletter/', include('yesimeanit.showoff.newsletter_subscriptions.urls')),
    url(r'', include('feincms.urls')),
)
