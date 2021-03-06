# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-19 20:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_id', models.IntegerField(default=None)),
                ('manager', models.ManyToManyField(default=None, related_name='manager_member', to=settings.AUTH_USER_MODEL)),
                ('member', models.ManyToManyField(default=None, related_name='group_member', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.CharField(max_length=160)),
                ('note', models.CharField(max_length=200)),
                ('feedback', models.CharField(max_length=200)),
                ('recurring', models.BooleanField()),
                ('start_date', models.DateField()),
                ('due_date', models.DateField()),
                ('status', models.CharField(choices=[('NEW', 'New'), ('INP', 'In Progress'), ('COM', 'Completed'), ('ONH', 'On Hold'), ('CAN', 'Cancelled')], default='NEW', max_length=3)),
                ('assigned_users', models.ManyToManyField(related_name='task_taker', to=settings.AUTH_USER_MODEL)),
                ('manager', models.ManyToManyField(related_name='task_manager', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(choices=[('IT', 'IT'), ('DE', 'Design')], default='IT', max_length=2)),
                ('title', models.CharField(max_length=160)),
                ('creation_time', models.DateTimeField()),
                ('update_time', models.DateTimeField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
