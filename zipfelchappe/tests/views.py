
from django.test import TestCase
from django.test.client import Client

from feincms.module.page.models import Page
from feincms.content.application.models import ApplicationContent

from bs4 import BeautifulSoup

from .factories import ProjectFactory, RewardFactory, PledgeFactory, UserFactory


class PledgeWorkflowTest(TestCase):

    def setUp(self):
        # feincms page containing zipfelchappe app content
        self.page = Page.objects.create(title='Projects', slug='projects')
        ct = self.page.content_type_for(ApplicationContent)
        ct.objects.create(parent=self.page, urlconf_path='zipfelchappe.urls')

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

    def assertRedirect(self, response, expected_url):
        """ Just check immediate redirect, don't follow target url """
        full_url = ('Location', 'http://testserver' + expected_url)
        self.assertEqual(response._headers['location'], full_url)
        self.assertEqual(response.status_code, 302)

    def test_project_list(self):
        """ Basic check if projects are visible in list """
        r = self.client.get('/projects/')
        self.assertEqual(200, r.status_code)
        soup = BeautifulSoup(str(r))

        # There should be two projects total
        project_links = soup.find_all('a', class_='project')
        self.assertEqual(2, len(project_links))

        # Check first project has correct url
        project1_url = self.project1.get_absolute_url()
        self.assertEqual(project_links[0]['href'], project1_url)

    def test_project_detail(self):
        """ Check if project detail page infos are correct """
        r = self.client.get(self.project1.get_absolute_url())
        self.assertEqual(200, r.status_code)
        soup = BeautifulSoup(str(r))

        # Project should not have any pledges yet
        achieved = soup.find(class_='progress').find(class_='info')
        self.assertEqual('0 CHF (0%)', achieved.text.strip())

        # Project should be backable
        back_button = soup.find(id='back_button')
        self.assertIsNotNone(back_button)

    def test_back_project(self):
        """ Does the back form show up the right way? """
        r = self.client.get('/projects/back/%s/' % self.project1.slug)

        # There should be a reward
        self.assertContains(r, 'testreward')

    def test_amount_fits_reward(self):
        """ Validation should prevent to small amounts for selected rewards """
        r = self.client.post('/projects/back/%s/' % self.project1.slug, {
            'project': self.project1.id,
            'amount': '10',
            'reward': self.reward.id
        })
        self.assertFormError(r, 'form', None, [
            'Amount is too small for reward!'
        ])

    def test_unavailable_rewards(self):
        # Validation should prevent to choose awards that are given away

        # Give away the limited reward
        PledgeFactory.create(
            project=self.project1,
            amount=25.00,
            reward=self.reward
        )

        # Try to create pledge with unavailable reward
        r = self.client.post('/projects/back/%s/' % self.project1.slug, {
            'project': self.project1.id,
            'amount': '20',
            'reward': self.reward.id
        })
        self.assertFormError(r, 'form', None, [
            'Sorry, this reward is not available anymore.'
        ])

    def test_pledge_with_login(self):
        # Submit pledge data
        r = self.client.post('/projects/back/%s/' % self.project1.slug, {
            'project': self.project1.id,
            'amount': '20',
            'reward': self.reward.id
        })

        # Should redirect to login page
        self.assertRedirect(r, '/projects/backer/authenticate/')

        # A pledge should now be associated with the session
        self.assertIn('pledge_id', self.client.session)

        # Submit data to login a existing user
        r = self.client.post('/projects/backer/login/', {
            'username': self.user.username,
            'password': 'test'
        })

        # We should then get redirect back to the authentication page
        self.assertRedirect(r, '/projects/backer/authenticate/')

        # Finally, we should get redirect to the payment viewew
        r = self.client.get('/projects/backer/authenticate/')
        self.assertRedirect(r, '/paypal/')
