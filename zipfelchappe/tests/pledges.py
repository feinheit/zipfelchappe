from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now

from django.core.exceptions import ValidationError

from .factories import ProjectFactory, PledgeFactory


class BasicPledgeTest(TestCase):

    def setUp(self):
        self.project = ProjectFactory.create()

        self.p1 = PledgeFactory.create(
            project=self.project,
            amount=10.00,
        )

    def test_cannot_change_project_end_date(self):
        self.project.end = now() + timedelta(days=7)
        self.assertRaises(ValidationError, self.project.full_clean)
