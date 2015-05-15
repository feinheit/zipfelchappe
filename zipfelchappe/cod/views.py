from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template import Context
from django.views.generic import View, TemplateView

from zipfelchappe.models import Pledge
from zipfelchappe.views import PledgeRequiredMixin
from zipfelchappe.emails import render_mail
from zipfelchappe.app_settings import MANAGERS

from .models import CodPayment
from .forms import RequestPaymentSlipForm

import logging
logger = logging.getLogger('zipfelchappe.cod')


class PaymentView(PledgeRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # update pledge status and create payment object
        self.pledge.status = Pledge.AUTHORIZED
        self.pledge.save()
        payment = CodPayment.objects.create(
            pledge=self.pledge,
            payment_slip_first_name=self.pledge.backer.first_name,
            payment_slip_last_name=self.pledge.backer.last_name
        )

        # send mail with payment info
        self.send_info_mail(request)

        # remove pledge id from session
        del self.request.session['pledge_id']

        initial_data = {'first_name': self.pledge.backer.first_name,
                        'last_name': self.pledge.backer.last_name,
                        'address': getattr(request.user, 'address', ''),
                        'zip_code': getattr(request.user, 'zip_code', ''),
                        'city': getattr(request.user, 'city', ''),
                        'payment': payment.pk}  # TODO: use UUID

        form = RequestPaymentSlipForm(initial=initial_data)

        # return confirmation
        return render(request, 'zipfelchappe/cod/confirmation.html', {
            'request_payment_slip_form': form,
            'pledge': self.pledge
        })

    def send_info_mail(self, request):
        # send mail with payment info
        context = Context({'request': request, 'pledge': self.pledge})
        subject, message = render_mail('cod_wiretransfer', context)

        send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL,
            [self.pledge.backer.email], fail_silently=False)


class RequestPaymentSlipView(View):
    """
    This view stores the customers address information and sends a mail to the project owner.
    """
    def post(self, request, *args, **kwargs):
        form = RequestPaymentSlipForm(request.POST)

        if form.is_valid():
            # update payment object
            payment = form.cleaned_data['payment']
            payment.payment_slip_requested = True
            payment.payment_slip_first_name = form.cleaned_data.get(
                'first_name')
            payment.payment_slip_last_name = form.cleaned_data.get('last_name')
            payment.payment_slip_address = form.cleaned_data.get('address')
            payment.payment_slip_zip_code = form.cleaned_data.get('zip_code')
            payment.payment_slip_city = form.cleaned_data.get('city')
            payment.save()
            # store the address in the user profile if the profile is empty.
            if request.user.is_authenticated():
                if hasattr(request.user, 'address') and hasattr(request.user, 'zip_code') \
                        and hasattr(request.user, 'city') and request.user.address == '':
                    request.user.address = payment.payment_slip_address
                    request.user.zip_code = payment.payment_slip_zip_code
                    request.user.city = payment.payment_slip_city
                    request.user.save()

            try:
                self.send_info_mail(payment)
            except IOError:
                logger.exception('Failed sending email to MANAGERS.')

            # show confirmation
            return redirect('zipfelchappe_cod_request_received')
        else:
            return render(
                request, 'zipfelchappe/cod/request_payment_slip_form.html',
                {'form': form}
            )

    def send_info_mail(self, payment):
        context = Context({'payment': payment})
        subject, message = render_mail('cod_payment_slip', context)
        receivers = [r[1] for r in MANAGERS]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, receivers, fail_silently=False)


class PaymentSlipRequestRecievedView(TemplateView):
    template_name = 'zipfelchappe/cod/payment_slip_confirmation.html'
