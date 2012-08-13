from django.conf.urls import patterns, url

urlpatterns = patterns('zipfelchappe.paypal.views',
    url(r'^$', 'payment', name='zipfelchappe_payment'),
    url(r'^ipn/$', 'ipn', name='zipfelchappe_paypal_ipn'),
)
