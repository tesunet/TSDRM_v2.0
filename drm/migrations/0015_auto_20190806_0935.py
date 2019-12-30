# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2019-08-06 09:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drm', '0014_knowledgefiledownload_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='HostsManage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host_ip', models.CharField(blank=True, max_length=50, null=True, verbose_name='主机IP')),
                ('os', models.CharField(blank=True, max_length=50, null=True, verbose_name='系统')),
                ('type', models.CharField(blank=True, max_length=20, null=True, verbose_name='连接类型')),
                ('username', models.CharField(blank=True, max_length=50, null=True, verbose_name='用户名')),
                ('password', models.CharField(blank=True, max_length=50, null=True, verbose_name='密码')),
            ],
        ),
        migrations.AddField(
            model_name='script',
            name='hosts_manage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='drm.HostsManage', verbose_name='主机管理'),
        ),
    ]
