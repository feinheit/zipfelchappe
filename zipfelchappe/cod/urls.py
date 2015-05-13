from django.conf.urls import patterns, url

from .views import PaymentView, RequestPaymentSlipView

urlpatterns = patterns('zipfelchappe.cod.views',
    url(r'^$', PaymentView.as_view(), name='zipfelchappe_cod_payment'),
    url(r'^request-payment-slip/$', RequestPaymentSlipView.as_view(),
        name='zipfelchappe_cod_payment_slip'),
)
