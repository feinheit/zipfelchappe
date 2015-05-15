from __future__ import absolute_import, unicode_literals
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.tests.utils import skipIfCustomUser

from feincms.module.page.models import Page
from feincms.content.application.models import ApplicationContent, app_reverse

from tests.factories import ProjectFactory, RewardFactory, UserFactory
from zipfelchappe import app_settings

@skipIfCustomUser
class PledgeWorkflowTest(TestCase):
    login_url = '/accounts/login/'

    def setUp(self):
        # feincms page containing zipfelchappe app content
        self.page = Page.objects.create(title='Projects', slug='projects')
        ct = self.page.content_type_for(ApplicationContent)
        ct.objects.create(parent=self.page, urlconf_path=app_settings.ROOT_URLS)

        # Fixture Data for following tests
        self.project1 = ProjectFactory.create()
        self.project2 = ProjectFactory.create()
        self.user = UserFactory.create()
        self.reward = RewardFactory.create(
            project=self.project1,
            minimum=20.00,
            quantity=2
        )

        # Fresh Client for every test
        self.client = Client()

    def tearDown(self):
        mail.outbox = []

    def assertRedirect(self, response, expected_url):
        """ Just check immediate redirect, don't follow target url """
        full_url = ('Location', 'http://testserver' + expected_url)
        self.assertIn('location', response._headers, 'Response from %s is not a redirect: %s'
                      % (expected_url, response.status_code))
        self.assertEqual(response._headers['location'], full_url,
                         'location expected: %s, actual: %s'
                         % (full_url, response._headers.get('location')))
        self.assertEqual(response.status_code, 302)

    def test_user_stays_logged_in(self):
        self.client.login(username=self.user, password='test')
        session_id = self.client.cookies['sessionid'].value
        response = self.client.get(self.project1.get_absolute_url())
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)
        back_url = app_reverse('zipfelchappe_backer_create', app_settings.ROOT_URLS,
                               kwargs={"slug": self.project1.slug})
        authenticate_url = app_reverse('zipfelchappe_backer_authenticate', app_settings.ROOT_URLS)
        payment_url = reverse('zipfelchappe_paypal_payment')
        thank_you_url = app_reverse('zipfelchappe_pledge_thankyou', app_settings.ROOT_URLS)
        backed_url = app_reverse('zipfelchappe_project_backed', app_settings.ROOT_URLS,
                                 kwargs={'slug': self.project1.slug})
        response = self.client.get(back_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

        response = self.client.post(back_url, {
            'project': self.project1.id,
            'amount': '20',
            'reward': self.reward.id,
            'provider': 'paypal',
            'accept_tac': True
        })
        self.assertRedirect(response, authenticate_url)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

        response = self.client.get(authenticate_url)
        self.assertRedirect(response, payment_url)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

        response = self.client.get(payment_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

        response = self.client.get(thank_you_url)
        self.assertRedirect(response, backed_url)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

        response = self.client.get(backed_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

        # back again
        response = self.client.get(back_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

        response = self.client.post(back_url, {
            'project': self.project1.id,
            'amount': '20',
            'reward': self.reward.id,
            'provider': 'paypal',
            'accept_tac': True
        })
        self.assertRedirect(response, authenticate_url)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

    def test_user_stays_logged_in_on_reload_before_payment(self):
        """ Here the user backs a project and then returns to the backing page before
            the payment process is completed.
        """
        self.client.login(username=self.user, password='test')
        session_id = self.client.cookies['sessionid'].value
        response = self.client.get(self.project1.get_absolute_url())
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)
        back_url = app_reverse('zipfelchappe_backer_create', app_settings.ROOT_URLS,
                               kwargs={"slug": self.project1.slug})
        authenticate_url = app_reverse('zipfelchappe_backer_authenticate', app_settings.ROOT_URLS)
        payment_url = reverse('zipfelchappe_paypal_payment')
        thank_you_url = app_reverse('zipfelchappe_pledge_thankyou', app_settings.ROOT_URLS)
        backed_url = app_reverse('zipfelchappe_project_backed', app_settings.ROOT_URLS,
                                 kwargs={'slug': self.project1.slug})
        response = self.client.get(back_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

        response = self.client.post(back_url, {
            'project': self.project1.id,
            'amount': '20',
            'reward': self.reward.id,
            'provider': 'paypal',
            'accept_tac': True
        })
        self.assertRedirect(response, authenticate_url)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

        response = self.client.get(authenticate_url)
        self.assertRedirect(response, payment_url)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

        response = self.client.get(payment_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

        # back again
        response = self.client.get(back_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

        response = self.client.post(back_url, {
            'project': self.project1.id,
            'amount': '20',
            'reward': self.reward.id,
            'provider': 'paypal',
            'accept_tac': True
        })
        self.assertRedirect(response, authenticate_url)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)