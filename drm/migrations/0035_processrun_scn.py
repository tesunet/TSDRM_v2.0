# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2019-09-20 13:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0034_auto_20190918_1937'),
    ]

    operations = [
        migrations.AddField(
            model_name='processrun',
            name='SCN',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='指定备份节点的SCN'),
        ),
    ]
