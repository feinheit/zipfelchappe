# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zipfelchappe', '0010_auto_20150513_1517'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('payment_received', models.DateField(verbose_name='payment received')),
                ('payment_slip_requested', models.BooleanField(default=False, verbose_name='payment slip requested')),
                ('payment_slip_sent', models.BooleanField(default=False, verbose_name='payment slip sent')),
                ('payment_slip_first_name', models.CharField(max_length=50, verbose_name='first_name', blank=True)),
                ('payment_slip_last_name', models.CharField(max_length=50, verbose_name='first_name', blank=True)),
                ('payment_slip_address', models.CharField(max_length=200, verbose_name='address', blank=True)),
                ('payment_slip_zip_code', models.CharField(max_length=20, verbose_name='zip_code', blank=True)),
                ('payment_slip_city', models.CharField(max_length=50, verbose_name='city', blank=True)),
                ('pledge', models.OneToOneField(related_name='cod_payment', to='zipfelchappe.Pledge')),
            ],
            options={
                'verbose_name': 'cod payments',
            },
            bases=(models.Model,),
        ),
    ]
