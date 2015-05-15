from django.conf.urls import url

from .views import PaymentView, RequestPaymentSlipView, PaymentSlipRequestRecievedView

urlpatterns = [
    url(r'^$', PaymentView.as_view(), name='zipfelchappe_cod_payment'),
    url(r'^request-payment-slip/$', RequestPaymentSlipView.as_view(),
        name='zipfelchappe_cod_payment_slip'),
    url(r'^request-payment-slip/ok/$', PaymentSlipRequestRecievedView.as_view(),
        name='zipfelchappe_cod_request_received'),
]
