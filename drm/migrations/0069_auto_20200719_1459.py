# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2020-07-19 14:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0068_cvclient_destination'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scriptinstance',
            name='origin',
        ),
        migrations.AddField(
            model_name='scriptinstance',
            name='primary',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='drm.CvClient', verbose_name='源端客户端'),
        ),
    ]