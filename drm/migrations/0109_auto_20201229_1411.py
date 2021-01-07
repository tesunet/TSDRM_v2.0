# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2020-12-29 14:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0108_auto_20201224_1700'),
    ]

    operations = [
        migrations.AddField(
            model_name='tsdrmjob',
            name='finalinput',
            field=models.TextField(blank=True, null=True, verbose_name='输入参数及值'),
        ),
        migrations.AddField(
            model_name='tsdrmjob',
            name='jobstepoutput',
            field=models.TextField(blank=True, null=True, verbose_name='每一步骤的输出参数及值'),
        ),
        migrations.AddField(
            model_name='tsdrmjob',
            name='jobvariable',
            field=models.TextField(blank=True, null=True, verbose_name='内部参数及值'),
        ),
    ]