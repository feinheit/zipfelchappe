
from datetime import timedelta

from django.utils import timezone

import factory

from ..models import Project, Reward, Pledge
from ..utils import get_backer_model

BackerModel = get_backer_model()


class ProjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Project

    title = factory.Sequence(lambda n: 'testproject %s' % n)
    slug = factory.Sequence(lambda n: 'test%s' % n)
    goal = 200.00
    currency = 'CHF'
    start = timezone.now()
    end = timezone.now() + timedelta(days=1)


class RewardFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Reward

    description = factory.Sequence(lambda n: 'testreward%s' % n)


class BackerFactory(factory.DjangoModelFactory):
    FACTORY_FOR = BackerModel


class PledgeFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Pledge

    status = Pledge.AUTHORIZED
    backer = factory.SubFactory(BackerFactory)
