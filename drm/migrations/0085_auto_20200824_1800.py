# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2020-08-24 18:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0084_zfssnapshot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='process',
            name='cv_client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='drm.HostsManage', verbose_name='关联客户端'),
        ),
    ]
