# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-23 04:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskList', '0005_auto_20180522_2115'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='rank',
            field=models.DateField(default=None),
        ),
    ]