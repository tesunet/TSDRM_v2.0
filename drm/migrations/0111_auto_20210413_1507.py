# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2021-04-13 15:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0110_auto_20210412_1203'),
    ]

    operations = [
        migrations.CreateModel(
            name='HostsProtection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protectiontype', models.CharField(blank=True, max_length=50, null=True, verbose_name='保护类型')),
                ('subtype', models.CharField(blank=True, max_length=50, null=True, verbose_name='保子类型')),
                ('info', models.TextField(default='<root></root>', null=True, verbose_name='保护相关信息')),
                ('state', models.CharField(blank=True, max_length=20, null=True, verbose_name='状态')),
            ],
        ),
        migrations.RemoveField(
            model_name='hostsmanage',
            name='os',
        ),
        migrations.RemoveField(
            model_name='hostsmanage',
            name='type',
        ),
        migrations.AddField(
            model_name='hostsmanage',
            name='host_type',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='主机类型'),
        ),
        migrations.AddField(
            model_name='hostsprotection',
            name='hostsmanage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='drm.HostsManage', verbose_name='客户端'),
        ),
    ]
