# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-09-05 01:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0004_auto_20180905_0922'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='verifyitems',
            name='steprun',
        ),
        migrations.AddField(
            model_name='verifyitemsrun',
            name='steprun',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='drm.StepRun'),
        ),
    ]
