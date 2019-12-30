# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-09-20 09:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0006_auto_20180905_1631'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='开始时间')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='结束时间')),
                ('purpose', models.CharField(blank=True, max_length=5000, null=True, verbose_name='演练目的')),
                ('process_run', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='drm.ProcessRun')),
            ],
        ),
    ]
