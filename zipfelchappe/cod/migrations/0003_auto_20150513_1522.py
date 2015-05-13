# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cod', '0002_auto_20150513_1518'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='codpayment',
            name='pledge',
        ),
        migrations.DeleteModel(
            name='CodPayment',
        ),
    ]
