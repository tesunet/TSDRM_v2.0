# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2020-07-13 15:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0064_auto_20200713_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostsmanage',
            name='config',
            field=models.TextField(default='<root></root>', null=True, verbose_name='主机参数'),
        ),
        migrations.AddField(
            model_name='hostsmanage',
            name='nodetype',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='节点类型'),
        ),
        migrations.AddField(
            model_name='hostsmanage',
            name='pnode',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='drm.HostsManage', verbose_name='父节点'),
        ),
        migrations.AddField(
            model_name='hostsmanage',
            name='sort',
            field=models.IntegerField(blank=True, null=True, verbose_name='排序'),
        ),
    ]
