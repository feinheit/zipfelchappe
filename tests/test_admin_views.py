# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.contrib.auth.tests.utils import skipIfCustomUser
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.utils import timezone
from feincms.module.page.models import Page
from feincms.content.application.models import ApplicationContent
from django.utils.translation import ugettext as _

from tests.factories import ProjectFactory, RewardFactory, PledgeFactory, UserFactory
from zipfelchappe import app_settings


@skipIfCustomUser
class AdminViewsTest(TestCase):
    def setUp(self):
        # feincms page containing zipfelchappe app content
        self.page = Page.objects.create(title='Projects', slug='projects')
        ct = self.page.content_type_for(ApplicationContent)
        ct.objects.create(parent=self.page, urlconf_path=app_settings.ROOT_URLS)

        # Fixture Data for following tests
        self.project1 = ProjectFactory.create()
        self.project2 = ProjectFactory.create()
        self.user = UserFactory.create()
        self.admin = UserFactory.create(is_superuser=True, is_staff=True)
        self.reward = RewardFactory.create(
            project=self.project1,
            minimum=20.00,
            quantity=1
        )

        # Fresh Client for every test
        self.client = Client()

    def test_collect_pledges(self):
        pledge1 = PledgeFactory.create(
            project=self.project1,
            amount=100.00,
            reward=self.reward,
        )
        pledge2 = PledgeFactory.create(
            project=self.project1,
            amount=150.00,
            reward=self.reward,
        )
        self.project1.end = timezone.now()
        self.project1.save()
        url = reverse('admin:zipfelchappe_project_collect_pledges',
                      kwargs={'project_id': self.project1.id})
        self.client.login(username=self.admin.username, password='test')

        self.assertTrue(self.project1.has_pledges)
        self.assertTrue(self.project1.is_financed)
        self.assertEquals(len(self.project1.collectable_pledges), 2)
        if hasattr(settings, 'ZIPFELCHAPPE_POSTFINANCE'):
            if settings['ZIPFELCHAPPE_POSTFINANCE']['LIVE']:
                raise AttributeError('Payment is live.')
        elif hasattr(settings, 'ZIPFELCHAPPE_PAYPAL'):
            if settings['ZIPFELCHAPPE_PAYPAL']['LIVE']:
                raise AttributeError('Payment is live.')

        # open the project detail page
        response = self.client.get('/admin/zipfelchappe/project/%s/' % self.project1.id)
        self.assertEquals(200, response.status_code)
        self.assertContains(response, _('Collect %(amount)s authorized pledges'
                                        % {'amount': 2}))

        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.assertContains(response, _('Collecting'))
        self.assertContains(response, self.project1.title)

    def test_change_view(self):
        self.client.login(username=self.admin.username, password='test')
        pledge1 = PledgeFactory.create(
            project=self.project1,
            amount=100.00,
            reward=self.reward,
        )
        url = reverse('admin:zipfelchappe_pledge_change', args=[pledge1.id])
        self.assertIsNotNone(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        url = reverse('admin:zipfelchappe_pledge_change', args=[100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)