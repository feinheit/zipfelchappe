from __future__ import absolute_import, unicode_literals
from django.core import mail
from django.test import TestCase
from django.test.client import Client
from django.utils import timezone
from django.contrib.auth.tests.utils import skipIfCustomUser

from feincms.module.page.models import Page
from feincms.content.application.models import ApplicationContent, app_reverse

from tests.factories import ProjectFactory, RewardFactory, PledgeFactory, UserFactory
from zipfelchappe.models import Backer, Pledge
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
            quantity=1
        )

        # Fresh Client for every test
        self.client = Client()

    def tearDown(self):
        mail.outbox = []

    def assertRedirect(self, response, expected_url):
        """ Just check immediate redirect, don't follow target url """
        full_url = ('Location', 'http://testserver' + expected_url)
        self.assertIn('location', response._headers)
        self.assertEqual(response._headers['location'], full_url)
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
        thank_you_url = app_reverse('zipfelchappe_pledge_thankyou', app_settings.ROOT_URLS)

        response = self.client.get(back_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

        response = self.client.post(back_url, {
            'project': self.project1.id,
            'amount': '20',
            'reward': self.reward.id,
            'provider': 'paypal'
        })
        self.assertRedirect(response, authenticate_url)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)

        response = self.client.get(back_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.client.cookies['sessionid'].value, session_id)
