# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2020-08-25 09:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0088_group_process'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='process',
            name='cv_client',
        ),
    ]
