# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2020-08-24 14:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0081_auto_20200824_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='scriptinstance',
            name='process',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='drm.Process', verbose_name='子流程(排错流程)'),
        ),
    ]
