# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2020-09-07 11:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0097_auto_20200901_1911'),
    ]

    operations = [
        migrations.AddField(
            model_name='kvmcopy',
            name='snapshot',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='所属快照'),
        ),
    ]