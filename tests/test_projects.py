from __future__ import unicode_literals, absolute_import
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.tests.utils import skipIfCustomUser

from django.utils import timezone
from django.test import TestCase
from django.core.exceptions import ValidationError
from zipfelchappe.models import Project, Pledge
from tests.factories import ProjectFactory, PledgeFactory
from zipfelchappe import app_settings
import zipfelchappe.payment_providers


@skipIfCustomUser
class BasicProjectTest(TestCase):

    def setUp(self):
        self.project = ProjectFactory.create()

        self.p1 = PledgeFactory.create(
            project=self.project,
            amount=10.00,
        )

        self.p2 = PledgeFactory.create(
            project=self.project,
            amount=20.00,
            anonymously=True
        )

    def tearDown(self):
        delete_candidates = [self.project, self.p1, self.p2]
        [obj.delete() for obj in delete_candidates if obj.id]

    def test_can_has_project(self):
        self.assertTrue(Project.objects.all().count() == 1)
        self.assertTrue(self.project.id is not None)

    def test_start_must_be_before_end(self):
        self.project.end = timezone.now() - timedelta(days=1)
        self.assertRaises(ValidationError, self.project.full_clean)

    def test_total_achieved_amount(self):
        self.assertEquals(self.project.achieved, Decimal('30.00'))

    def test_total_achieved_percent(self):
        self.assertEquals(self.project.percent, Decimal('15.00'))

    def test_can_change_currency_without_pledges(self):
        self.p1.delete()
        self.p2.delete()
        self.project.currency = 'EUR'

        try:
            self.project.full_clean()
        except ValidationError:
            self.fail("Could not change currency while having no pledges")

    def test_cannot_change_currency_with_pledges(self):
        self.project.currency = 'EUR'
        self.assertRaises(ValidationError, self.project.full_clean)

    def test_unauthorized_pledges(self):
        self.p1.status = Pledge.UNAUTHORIZED
        self.p1.save()
        self.p2.status = Pledge.UNAUTHORIZED
        self.p2.save()

        self.assertEquals(self.project.achieved, Decimal('0.00'))
        self.assertEquals(self.project.percent, 0)

    def test_cannot_change_goal_with_pledges(self):
        self.project.goal = 50
        self.assertRaises(ValidationError, self.project.full_clean)

    def test_properties(self):
        self.assertEquals(len(self.project.authorized_pledges), 2)
        self.assertEquals(len(self.project.collectable_pledges), 2)
        self.assertTrue(self.project.has_pledges)
        self.assertEquals(self.project.achieved, 30)
        self.assertTrue(isinstance(self.project.achieved, Decimal))
        self.assertEquals(self.project.percent, 15)
        self.assertEquals(self.project.goal_display, '200 CHF')
        self.assertEquals(self.project.achieved_display, '30 CHF (15%)')
        self.assertTrue(self.project.is_active)
        self.assertFalse(self.project.is_financed)
        self.assertFalse(self.project.ended_successfully)
        self.assertEquals(self.project.update_count, 0)
        self.assertEquals(len(self.project.public_pledges), 1)

    def test_default_max_duration(self):
        pf = zipfelchappe.payment_providers['postfinance']
        del zipfelchappe.payment_providers['postfinance']
        project = ProjectFactory.create()
        self.assertEqual(app_settings.MAX_PROJECT_DURATION_DAYS, 120)
        project.end = timezone.now() + timedelta(days=121)
        self.assertRaises(ValidationError, project.full_clean)
        project.end = timezone.now() + timedelta(days=119)
        project.full_clean()
        zipfelchappe.payment_providers['postfinance'] = pf

    def test_postfinance_max_duration(self):
        now = timezone.now()
        project = ProjectFactory.create(start=now)
        project.end = now + timedelta(days=31)
        self.assertRaises(ValidationError, project.full_clean)
        project.end = now + timedelta(days=29)
        project.full_clean()
