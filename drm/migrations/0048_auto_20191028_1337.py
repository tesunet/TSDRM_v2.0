# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2019-10-28 13:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0047_auto_20191028_0903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='origin',
            name='data_path',
            field=models.CharField(blank=True, default='', max_length=512, verbose_name='数据文件重定向路径'),
        ),
    ]
