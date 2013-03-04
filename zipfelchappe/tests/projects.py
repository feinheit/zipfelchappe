import unittest
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ..models import Project, Pledge
from ..utils import get_backer_model

BackerModel = get_backer_model()

class BasicProjectTest(unittest.TestCase):

    def setUp(self):
        self.project = Project.objects.create(
            title = u'TestProject',
            slug = u'test',
            goal = 200.00,
            currency = 'CHF',
            start = timezone.now(),
            end = timezone.now() + timedelta(days=1)
        )

        self.backer = BackerModel.objects.create()

        self.p1 = Pledge.objects.create(
            status = Pledge.AUTHORIZED,
            backer = self.backer,
            project = self.project,
            amount = 10.00,
        )

        self.p2 = Pledge.objects.create(
            status = Pledge.AUTHORIZED,
            backer = self.backer,
            project = self.project,
            amount = 20.00,
        )

    def tearDown(self):
        delete_candidates = [
            self.project,
            self.backer,
            self.p1,
            self.p2
        ]

        for obj in delete_candidates:
            if obj.id:
                obj.delete()

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
            self.fail("Could change currency while having pledges")

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