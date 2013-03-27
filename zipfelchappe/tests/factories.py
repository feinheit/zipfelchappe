
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.models import User

import factory

from ..models import Project, Reward, Backer, Pledge


class ProjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Project

    title = factory.Sequence(lambda n: 'Testproject %s' % n)
    slug = factory.Sequence(lambda n: 'test%s' % n)
    goal = 200.00
    currency = 'CHF'
    start = timezone.now()
    end = timezone.now() + timedelta(days=1)


class RewardFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Reward

    description = factory.Sequence(lambda n: 'testreward%s' % n)


class BackerFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Backer


class PledgeFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Pledge

    status = Pledge.AUTHORIZED
    backer = factory.SubFactory(BackerFactory)


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: 'user%s' % n)
    email = factory.Sequence(lambda n: 'user%s@example.org' % n)
    is_active = True
    is_superuser = False
    is_staff = False
    # password 'test'
    password = 'pbkdf2_sha256$10000$s9Ed0KfEQgTY$CsbbUpXaWk+8eAB+Oga2hBqD82kU4vl+QQaqr/wCZXY='