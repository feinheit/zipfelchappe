import unittest
from datetime import timedelta
from django.utils import timezone

from django.core.exceptions import ValidationError

from ..models import Project, Reward, Pledge
from ..utils import get_backer_model

BackerModel = get_backer_model()


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
