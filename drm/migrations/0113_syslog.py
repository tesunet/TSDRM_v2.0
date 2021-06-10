# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2021-04-27 16:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('drm', '0112_hostsmanage_monitor'),
    ]

    operations = [
        migrations.CreateModel(
            name='SysLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datatime', models.DateTimeField(blank=True, null=True, verbose_name='创建时间')),
                ('state', models.CharField(blank=True, max_length=20, null=True, verbose_name='状态')),
                ('content', models.TextField(blank=True, null=True, verbose_name='内容')),
                ('type', models.CharField(choices=[('login', '登录'), ('new', '新增'), ('edit', '修改'), ('delete', '删除'), ('other', '其他')], default='other', max_length=20, null=True, verbose_name='类型')),
                ('userid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
        ),
    ]