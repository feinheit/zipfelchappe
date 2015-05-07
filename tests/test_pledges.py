from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from tests.factories import ProjectFactory, PledgeFactory
from zipfelchappe.models import Pledge


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

    def test_mark_failed(self):
        self.assertEquals(self.p1.status, Pledge.AUTHORIZED)
        self.assertEquals('', self.p1.extradata)
        self.p1.mark_failed('oops')
        self.assertEquals(self.p1.status, Pledge.FAILED)
        self.assertEquals(self.p1.details, 'oops\n')
        self.assertEquals(self.p1.reward, None)
