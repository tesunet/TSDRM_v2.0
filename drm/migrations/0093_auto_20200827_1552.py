# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2020-08-27 15:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0092_auto_20200825_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kvmcopy',
            name='create_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人'),
        ),
    ]
