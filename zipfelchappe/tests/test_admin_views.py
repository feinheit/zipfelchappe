# coding: utf-8
from __future__ import absolute_import, unicode_literals
from unittest import skip
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from feincms.module.page.models import Page
from feincms.content.application.models import ApplicationContent

from .factories import ProjectFactory, RewardFactory, PledgeFactory, UserFactory
from ..models import Backer
from zipfelchappe import app_settings


class AdminViewsTest(TestCase):
    def setUp(self):
        # feincms page containing zipfelchappe app content
        self.page = Page.objects.create(title='Projects', slug='projects')
        ct = self.page.content_type_for(ApplicationContent)
        ct.objects.create(parent=self.page, urlconf_path='zipfelchappe.urls')

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

    @skip('Reverse not working.')
    def test_collect_pledges(self):
        pledge = PledgeFactory.create(
            project=self.project1,
            amount=25.00,
            reward=self.reward
        )
        url = reverse('admin:zipfelchappe_project_collect_pledges',
                      kwargs={'project_id': self.project1.id})
        self.client.login(username=self.admin.username, password='test')
        self.fail('TODO')