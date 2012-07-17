import unittest
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Project, Reward, Pledge
from .utils import get_backer_model

BackerModel = get_backer_model()

# TODO: Maybe better use fixtures?

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

class BasicRewardTest(unittest.TestCase):

    def setUp(self):
        self.project = Project.objects.create(
            title = u'RewardProject',
            slug = u'test',
            goal = 200.00,
            currency = 'CHF',
            start = timezone.now(),
            end = timezone.now() + timedelta(days=1)
        )

        self.reward = Reward.objects.create(
            project = self.project,
            title = 'TestReward',
            minimum = 20.00,
            description = 'TestReward',
            quantity = 5
        )

        self.backer = BackerModel.objects.create()

        self.p1 = Pledge.objects.create(
            status = Pledge.AUTHORIZED,
            backer = self.backer,
            project = self.project,
            amount = 25.00,
            reward = self.reward
        )

        # Payment is not saved yet
        self.p2 = Pledge(
            status = Pledge.AUTHORIZED,
            backer = self.backer,
            project = self.project,
            amount = 20.00,
            reward = self.reward
        )

    def tearDown(self):
        delete_candidates = [
            self.project,
            self.backer,
            self.reward,
            self.p1,
            self.p2,
        ]

        for obj in delete_candidates:
            if obj.id:
                obj.delete()

    def test_can_has_rewards(self):
        self.assertTrue(Reward.objects.all().count() == 1)
        self.assertTrue(self.reward.id is not None)

    def test_awarded(self):
        self.assertEquals(self.reward.awarded, 1)
        self.p2.save()
        self.assertEquals(self.reward.awarded, 2)

    def test_available(self):
        self.assertEquals(self.reward.available, 4)
        self.p2.save()
        self.assertEquals(self.reward.available, 3)

    def test_quantity_to_low(self):
        self.p2.save()

        # That's ok, we have given away this reward only twice
        self.reward.quantity = 4
        try:
            self.reward.full_clean()
        except ValidationError:
            self.fail('Could not reduce quantity to 4')

        # That's too low
        self.reward.quantity = 1
        self.assertRaises(ValidationError, self.reward.full_clean)
