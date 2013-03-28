from django.conf.urls import patterns, url

urlpatterns = patterns('zipfelchappe.postfinance.views',
    url(r'^$', 'payment', name='zipfelchappe_postfinance_payment'),
    url(r'^ipn/$', 'ipn', name='zipfelchappe_postfinance_ipn'),
)
