from django.conf.urls import patterns, url

urlpatterns = patterns('zipfelchappe.paypal.views',
    url(r'^ipn/$', 'ipn', name='zipfelchappe_paypal_ipn'),

    url(r'^$', 'payment', name='zipfelchappe_paypal_payment'),
    url(r'^/thankyou/$', 'thankyou', name='zipfelchappe_paypal_thankyou'),
    url(r'^canceled/$', 'canceled', name='zipfelchappe_paypal_canceled'),
)
