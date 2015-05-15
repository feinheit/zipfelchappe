# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.tests.utils import skipIfCustomUser
from django.test import TestCase, Client
from feincms.content.application.models import ApplicationContent
from feincms.module.page.models import Page
from tests.factories import ProjectFactory, PledgeFactory, UserFactory
from zipfelchappe import app_settings
from importlib import import_module
from django.conf import settings
from zipfelchappe.cod.models import CodPayment
from zipfelchappe.models import Pledge
from .factories import CodPaymentFactory


@skipIfCustomUser
class CodTest(TestCase):
    fixtures = ['sites_test.json']

    def setUp(self):
        # feincms page containing zipfelchappe app content
        self.page = Page.objects.create(title='Projects', slug='projects', override_url='/')
        ct = self.page.content_type_for(ApplicationContent)
        ct.objects.create(parent=self.page, urlconf_path=app_settings.ROOT_URLS)

        self.project = ProjectFactory.create()
        self.p1 = PledgeFactory.create(
            project=self.project,
            amount=10,
            provider='postfinance'
        )
        self.user = UserFactory.create(
            first_name='Hans',
            last_name='Muster'
        )
        self.p1.backer.user = self.user
        self.p1.backer.save()
        self.client = self.get_client_with_session()

    def tearDown(self):
        mail.outbox = []

    def get_client_with_session(self):
        client = Client()
        engine = import_module(settings.SESSION_ENGINE)
        s = engine.SessionStore()
        s.save()
        client.cookies[settings.SESSION_COOKIE_NAME] = s.session_key
        return client

    def test_payment_view(self):
        session = self.client.session
        session['pledge_id'] = str(self.p1.id)
        session.save()
        # There is no payment object yet.
        self.assertEqual(0, CodPayment.objects.filter(pledge=self.p1).count())
        self.client.login(username=self.user, password='test')
        url = reverse('zipfelchappe_cod_payment')
        post_url = reverse('zipfelchappe_cod_payment_slip')
        response = self.client.get(url)
        # the user can request a payment slip
        self.assertContains(response, 'Request a payment slip')
        # the name is filled in
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)
        self.assertContains(response, 'action="%s"' % post_url)
        # the pledge has been deleted from the session
        self.assertNotIn('pledge_id', self.client.session)
        # an email has been sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Payment instructions for %s' % self.p1.project)
        self.assertEqual(email.to, [self.user.email])
        self.assertIn(self.user.first_name, email.body)
        self.assertIn(self.user.last_name, email.body)

        # The pledge is marked as AUTHORIZED
        self.assertEqual(self.p1.status, Pledge.AUTHORIZED)

        # a CodPayment object has been created
        payment = CodPayment.objects.get(pledge=self.p1)
        self.assertEqual(payment.payment_slip_first_name, self.user.first_name)
        self.assertEqual(payment.payment_slip_last_name, self.user.last_name)
        self.assertFalse(payment.payment_slip_requested)
        self.assertFalse(payment.payment_slip_sent)
        self.assertIsNone(payment.payment_received)

    def test_request_payment_slip(self):
        self.client.login(username=self.user, password='test')
        payment = CodPaymentFactory.create(
            pledge=self.p1,
            payment_slip_first_name=self.user.first_name,
            payment_slip_last_name=self.user.last_name
        )
        url = reverse('zipfelchappe_cod_payment_slip')
        success_url = reverse('zipfelchappe_cod_request_received')

        args = {
            'payment': payment.id,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'address': '1 infinite loop',
            'zip_code': '8004',
            'city': 'Zürich'
        }
        # post the form
        response = self.client.post(url, args)
        self.assertRedirects(response, success_url)
        # The address has been added to the payment
        payment = CodPayment.objects.get(pledge=self.p1)
        self.assertEquals(payment.payment_slip_address, '1 infinite loop')
        self.assertEquals(payment.payment_slip_zip_code, '8004')
        self.assertEquals(payment.payment_slip_city, 'Zürich')
        self.assertTrue(payment.payment_slip_requested)


        # a mail has been sent to the admins
        # an email has been sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Someone requested a payment slip')
        self.assertEqual(email.to, [app_settings.MANAGERS[0][1]])
        self.assertIn(self.user.first_name, email.body)
        self.assertIn(self.user.last_name, email.body)
        self.assertIn('1 infinite loop', email.body)
        self.assertIn('Zürich', email.body)
        self.assertIn('8004', email.body)
