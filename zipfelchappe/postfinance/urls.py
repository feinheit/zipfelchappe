from django.conf.urls import patterns, url

urlpatterns = patterns('zipfelchappe.postfinance.views',
    url(r'^$', 'payment', name='zipfelchappe_postfinance_payment'),
    url(r'^declined/$', 'payment_declined', name='zipfelchappe_postfinance_declined'),
    url(r'^exception/$', 'payment_exception', name='zipfelchappe_postfinance_exception'),
    url(r'^ipn/$', 'ipn', name='zipfelchappe_postfinance_ipn'),
)
