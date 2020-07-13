# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2020-07-13 12:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0063_origin_utils'),
    ]

    operations = [
        migrations.AddField(
            model_name='origin',
            name='log_restore',
            field=models.IntegerField(choices=[(1, '是'), (2, '否')], default=1, null=True, verbose_name='是否回滚日志'),
        ),
        migrations.AddField(
            model_name='target',
            name='utils',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='drm.UtilsManage', verbose_name='关联工具'),
        ),
    ]