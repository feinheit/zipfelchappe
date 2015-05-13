from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import View
from django.utils.translation import ugettext_lazy as _

from zipfelchappe.models import Pledge
from zipfelchappe.views import PledgeRequiredMixin

from .models import CodPayment
from .forms import RequestPaymentSlipForm


class PaymentView(PledgeRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # update pledge status and create payment object
        self.pledge.status = Pledge.AUTHORIZED
        self.pledge.save()
        self.payment = CodPayment.objects.create(pledge=self.pledge)

        # send mail with payment info
        mail_content = render_to_string(
            'zipfelchappe/cod/emails/payment_info.txt',
            {
                'request': request,
                'pledge': self.pledge,
            })
        lines = mail_content.splitlines()
        subject = lines[0]
        body = '\n'.join(lines[1:])
        send_mail(
            subject, body, settings.DEFAULT_FROM_EMAIL,
            [self.pledge.backer.user.email], fail_silently=False)

        # remove pledge id from session
        del self.request.session['pledge_id']

        # return confirmation
        return render(request, 'zipfelchappe/cod/confirmation.html', {
            'request_payment_slip_form': RequestPaymentSlipForm(initial={
                'payment': self.payment.pk,
                'first_name': self.pledge.backer.first_name,
                'last_name': self.pledge.backer.last_name,
            })
        })


class RequestPaymentSlipView(View):
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

            # TODO: inform admins that a slip was requested

            # show confirmation
            return render(
                request, 'zipfelchappe/cod/payment_slip_confirmation.html')
        else:
            return render(
                request, 'zipfelchappe/cod/request_payment_slip_form.html',
                {'form': form}
            )
