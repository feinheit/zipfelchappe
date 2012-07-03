import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from zipfelchappe.models import Project, Reward, Payment

class BasicProjectTest(unittest.TestCase):
    
    def setUp(self):
        self.project = Project.objects.create(
            title = u'TestProject',
            slug = u'test',
            goal = 10000.00,
            currency = 'CHF',
            start = datetime.now(),
            end = datetime.now() + timedelta(days=1)
        )
        
        self.user = User.objects.create(username='user')
        
    def tearDown(self):
        self.project.delete()
        self.user.delete()
    
    def test_can_has_project(self):        
        self.assertTrue(Project.objects.all().count() == 1)
        self.assertTrue(self.project.id is not None)
        
    def test_start_must_be_before_end(self):
        self.project.end = datetime.now() - timedelta(days=1)
        self.assertRaises(ValidationError, self.project.full_clean)
        
    def test_total_achieved_amount(self):
        payment1 = Payment.objects.create(
            user = self.user,
            project = self.project,
            amount = 10.00,
        )
        
        payment2 = Payment.objects.create(
            user = self.user,
            project = self.project,
            amount = 20.00,
        )
        
        self.assertEquals(self.project.achieved, Decimal('30.00'))
        
        payment1.delete()
        payment2.delete()
