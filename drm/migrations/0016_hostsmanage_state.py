# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2019-08-06 11:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0015_auto_20190806_0935'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostsmanage',
            name='state',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='状态'),
        ),
    ]
