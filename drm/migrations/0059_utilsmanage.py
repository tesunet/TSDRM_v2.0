# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2020-06-23 09:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0058_processrun_rto'),
    ]

    operations = [
        migrations.CreateModel(
            name='UtilsManage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('util_type', models.CharField(default='', max_length=128, null=True, verbose_name='工具类型')),
                ('code', models.CharField(default='', max_length=128, null=True, verbose_name='工具编号')),
                ('name', models.CharField(default='', max_length=128, null=True, verbose_name='工具编号')),
                ('content', models.TextField(default='', null=True, verbose_name='内容')),
                ('state', models.CharField(blank=True, max_length=20, null=True, verbose_name='状态')),
            ],
        ),
    ]
