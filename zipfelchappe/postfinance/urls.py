from __future__ import unicode_literals, absolute_import
from django.conf.urls import patterns, url
from . import views

urlpatterns = [
    url(r'^$', views.payment, name='zipfelchappe_postfinance_payment'),
    url(r'^declined/$', views.payment_declined, name='zipfelchappe_postfinance_declined'),
    url(r'^exception/$', views.payment_exception, name='zipfelchappe_postfinance_exception'),
    url(r'^ipn/$', views.ipn, name='zipfelchappe_postfinance_ipn'),
]
