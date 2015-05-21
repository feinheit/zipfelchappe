# coding: utf-8
""" This module contains event handlers that can be used to react to different events such as
    a user signing up.
"""

from __future__ import absolute_import, unicode_literals
from .models import Backer, Pledge


def create_backer(sender, **kwargs):
    """
    This handler can be used to create a Backer instance during the registration process.
    This allows to assign a pledge to a user before he has finished the registration process.
    This way the user can continue the backing flow even if he uses a different browser to
    confirm the registration link than the one he registered.

    The following example is for the use with django-allauth::

        from allauth.account.signals import user_signed_up

        user_signed_up.connect(create_backer)

    :param sender: accounts.User (not used)
    :param kwargs: kwargs must contain a request and a user instance.
    """
    user = kwargs.get('user')
    pledge_id = kwargs['request'].session.get('pledge_id')
    if user and pledge_id:
        backer, created = Backer.objects.get_or_create(user=user)
        pledge = Pledge.objects.get(id=pledge_id)
        pledge.set_backer(backer)
        pledge.save()
