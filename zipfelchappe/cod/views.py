from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.template import Context
from django.views.generic import View
from zipfelchappe.app_settings import USER_FIRST_NAME_FIELD, USER_LAST_NAME_FIELD

from zipfelchappe.models import Pledge
from zipfelchappe.views import PledgeRequiredMixin
from zipfelchappe.emails import render_mail

from .models import CodPayment
from .forms import RequestPaymentSlipForm



class PaymentView(PledgeRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # update pledge status and create payment object
        self.pledge.status = Pledge.AUTHORIZED
        self.pledge.save()
        self.payment = CodPayment.objects.create(pledge=self.pledge)

        # send mail with payment info
        self.send_info_mail(request)

        # remove pledge id from session
        del self.request.session['pledge_id']

        initial_data = {'first_name': getattr(request.user, USER_FIRST_NAME_FIELD, ''),
                        'last_name': getattr(request.user, USER_LAST_NAME_FIELD, ''),
                        'address': getattr(request.user, 'address', ''),
                        'zip_code': getattr(request.user, 'zip_code', ''),
                        'city': getattr(request.user, 'city', ''),
                        'payment': self.payment.pk}

        form = RequestPaymentSlipForm(initial=initial_data)

        # return confirmation
        return render(request, 'zipfelchappe/cod/confirmation.html', {
            'request_payment_slip_form': form
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

            # TODO: inform admins that a slip was requested

            # show confirmation
            return render(
                request, 'zipfelchappe/cod/payment_slip_confirmation.html')
        else:
            return render(
                request, 'zipfelchappe/cod/request_payment_slip_form.html',
                {'form': form}
            )
