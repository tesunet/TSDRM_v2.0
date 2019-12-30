# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2019-10-14 13:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0044_auto_20191009_2149'),
    ]

    operations = [
        migrations.AddField(
            model_name='step',
            name='force_exec',
            field=models.IntegerField(choices=[(1, '是'), (2, '否')], default=2, null=True, verbose_name='流程关闭时强制执行'),
        ),
    ]
