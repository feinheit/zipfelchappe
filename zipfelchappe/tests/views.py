
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.client import Client

from feincms.module.page.models import Page
from feincms.content.application.models import ApplicationContent

from bs4 import BeautifulSoup

from ..models import Project, Pledge
from ..utils import get_backer_model

from .factories import ProjectFactory, RewardFactory, PledgeFactory, UserFactory


class PledgeWorkflowTest(TestCase):

    def setUp(self):
        # feincms page containing zipfelchappe app content
        self.page = Page.objects.create(title = 'Projects', slug = 'projects')
        ct = self.page.content_type_for(ApplicationContent)
        ct.objects.create(parent=self.page, urlconf_path='zipfelchappe.urls')

        self.project1 = ProjectFactory.create()
        self.project2 = ProjectFactory.create()
        self.reward = RewardFactory.create(
            project = self.project1,
            minimum = 20.00,
        )

        self.user = UserFactory.create()

    def assertRedirect(self, response, expected_url):
        """ Just check immediate redirect, don't follow target url """
        full_url = ('Location', 'http://testserver' + expected_url)
        self.assertEqual(response._headers['location'], full_url)
        self.assertEqual(response.status_code, 302)

    def testWithLogin(self):
        c = Client()

        ## Project list view ##
        r = c.get('/projects/')
        self.assertEqual(200, r.status_code)
        soup = BeautifulSoup(str(r))

        # There should be two projects total
        project_links = soup.find_all('a', class_='project')
        self.assertEqual(2, len(project_links))

        # Check first project has correct url
        project1_url = self.project1.get_absolute_url()
        self.assertEqual(project_links[0]['href'], project1_url)

        ## Project detail view ##
        r = c.get(project1_url)
        self.assertEqual(200, r.status_code)
        soup = BeautifulSoup(str(r))

        # Project should not have any pledges yet
        achieved = soup.find(class_='progress').find(class_='info')
        self.assertEqual('0 CHF (0%)', achieved.text.strip())

        # Project should be backable
        back_button = soup.find(id='back_button')
        self.assertIsNotNone(back_button)

        # Find "back this project" link
        back_project_link = back_button.parent['href']
        self.assertIsNotNone(back_project_link)

        ## Back project view ##
        r = c.get(back_project_link)

        # There should be a reward
        self.assertIn('testreward', str(r))

        # Submit pledge data
        r = c.post(back_project_link, {
            'project': self.project1.id,
            'amount': '20',
            'reward': self.reward.id
        })

        # Should be redirect to login page
        self.assertRedirect(r, '/projects/backer/authenticate/')

        # A pledge should now be associated with the session
        self.assertIn('pledge_id', c.session)

        # Submit data to login a existing user
        r = c.post('/projects/backer/login/', {
            'username': self.user.username,
            'password': 'test'
        })

        # We should then get redirect back to the authentication page
        self.assertRedirect(r, '/projects/backer/authenticate/')

        # Finally, we should get redirect to the payment viewew
        r = c.get('/projects/backer/authenticate/')
        self.assertRedirect(r, '/paypal/')