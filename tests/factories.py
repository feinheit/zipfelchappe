from __future__ import absolute_import, unicode_literals
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model
import factory

from zipfelchappe.models import Project, Reward, Backer, Pledge


class ProjectFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Testproject %s' % n)
    slug = factory.Sequence(lambda n: 'test%s' % n)
    goal = 200.00
    currency = 'CHF'
    start = timezone.now()
    end = timezone.now() + timedelta(days=1)

    class Meta:
        model = Project


class RewardFactory(factory.DjangoModelFactory):
    description = factory.Sequence(lambda n: 'testreward%s' % n)

    class Meta:
        model = Reward


class BackerFactory(factory.DjangoModelFactory):
    class Meta:
        model = Backer


class PledgeFactory(factory.DjangoModelFactory):
    status = Pledge.AUTHORIZED
    backer = factory.SubFactory(BackerFactory)

    class Meta:
        model = Pledge


class UserFactory(factory.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'user%s' % n)
    email = factory.Sequence(lambda n: 'user%s@example.org' % n)
    is_active = True
    is_superuser = False
    is_staff = False
    # password 'test'
    password = 'pbkdf2_sha256$10000$s9Ed0KfEQgTY$CsbbUpXaWk+8eAB+Oga2hBqD82kU4vl+QQaqr/wCZXY='

    class Meta:
        model = get_user_model()
