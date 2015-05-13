# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cod', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codpayment',
            name='payment_received',
            field=models.DateField(null=True, verbose_name='payment received'),
            preserve_default=True,
        ),
    ]
