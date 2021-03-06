# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-23 20:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskList', '0012_auto_20180523_2026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recurringtask',
            name='due_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='recurringtask',
            name='recurr_last_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='repeats',
            field=models.CharField(blank=True, choices=[('NONE', 'no repeat'), ('YEAR', 'every year'), ('MONT', 'every month'), ('WEEK', 'every week'), ('DAIL', 'every day')], default='NONE', max_length=4),
        ),
        migrations.AlterField(
            model_name='task',
            name='start_date',
            field=models.DateField(blank=True),
        ),
    ]
