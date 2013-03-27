import unittest

from django.core.exceptions import ValidationError

from ..models import Reward

from .factories import ProjectFactory, RewardFactory, PledgeFactory


class BasicRewardTest(unittest.TestCase):

    def setUp(self):
        self.project = ProjectFactory.create()

        self.reward = RewardFactory.create(
            project = self.project,
            minimum = 20.00,
            quantity = 5
        )

        self.p1 = PledgeFactory.create(
            project = self.project,
            amount = 25.00,
            reward = self.reward
        )

        # Payment is not saved yet
        self.p2 = PledgeFactory.build(
            project = self.project,
            amount = 20.00,
            reward = self.reward
        )

    def tearDown(self):
        delete_candidates = [self.project, self.reward, self.p1, self.p2]
        [obj.delete() for obj in delete_candidates if obj.id]

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
