# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2020-08-24 13:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0080_kvmmachine'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kvmmachine',
            name='filesystem',
            field=models.TextField(blank=True, null=True, verbose_name='kvm虚拟机文件系统路径'),
        ),
    ]