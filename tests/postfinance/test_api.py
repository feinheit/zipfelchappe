# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.tests.utils import skipIfCustomUser
from django.test import TestCase, Client
from feincms.content.application.models import ApplicationContent, app_reverse
from feincms.module.page.models import Page
from tests.factories import ProjectFactory, PledgeFactory, UserFactory
from zipfelchappe import app_settings
from importlib import import_module
from django.conf import settings

# https://e-payment.postfinance.ch/ncol/test/testsha.asp

@skipIfCustomUser
class PostfinanceApiTest(TestCase):

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
        url = reverse('zipfelchappe_postfinance_payment')
        self.assertIsNotNone(url)
        # call the view
        response = self.client.get(url)
        # print response
        # check the response
        self.assertEqual(self.client.session['pledge_id'], str(self.p1.id))
        self.assertNotEquals('', self.user.email)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, '<form method="post" action="https://e-payment.postfinance.ch/ncol/test/orderstandard.asp"')
        self.assertContains(response, '<input type="hidden" name="ORDERID" value="%s-%s" />'
                            % (self.project.slug, self.p1.id))
        # Amount is in cents
        self.assertContains(response, '<input type="hidden" name="AMOUNT" value="1000" />')
        self.assertContains(response, '<input type="hidden" name="CN" value="Hans Muster" />')
        self.assertContains(response, '<input type="hidden" name="EMAIL" value="%s" />'
                            % self.user.email)
        self.assertContains(response, '<input type="hidden" name="COM" value="%s"/>'
                            % 'Pledge of 10 CHF from Hans Muster to Testproject %i' % self.p1.id)
        self.assertContains(response, '<input type="hidden" name="ACCEPTURL" value="%s" />'
                            % 'http://example.com/pledge/thankyou/')
        self.assertContains(response, '<input type="hidden" name="DECLINEURL" value="%s" />'
                            % 'http://example.com/postfinance/declined/')
        self.assertContains(response, '<input type="hidden" name="EXCEPTIONURL" value="%s" />'
                            % 'http://example.com/postfinance/exception/')
        self.assertContains(response, '<input type="hidden" name="CANCELURL" value="%s" />'
                            % 'http://example.com/pledge/cancel/')


    def test_decline_view(self):
        pass


    # def test_exception_view(self):
    #     self.fail()
    #
    #
    # def test_cancel_view(self):
    #     self.fail()
    #
    #
    # def test_ipn_view(self):
    #     self.fail()