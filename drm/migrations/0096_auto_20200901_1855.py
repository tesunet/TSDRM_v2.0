# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2020-09-01 18:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0095_remove_process_nodetype'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='procosstype',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='预案类型'),
        ),
        migrations.AlterField(
            model_name='process',
            name='type',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='客户端类型'),
        ),
    ]