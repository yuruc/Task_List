# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-23 05:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskList', '0008_auto_20180523_0508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='rank',
            field=models.BigIntegerField(blank=True, default=None),
        ),
    ]
