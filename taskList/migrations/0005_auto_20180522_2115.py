# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-22 21:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskList', '0004_auto_20180522_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='repeats',
            field=models.CharField(blank=True, choices=[('YEAR', 'every year'), ('MONT', 'every month'), ('WEEK', 'every week'), ('DAIL', 'every day')], max_length=4),
        ),
    ]