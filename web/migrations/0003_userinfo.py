# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2019-04-07 15:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0001_initial'),
        ('web', '0002_depart'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pwd', models.CharField(default='', max_length=64, verbose_name='密码')),
                ('name', models.CharField(max_length=32, verbose_name='用户姓名')),
                ('phone', models.CharField(max_length=32, verbose_name='电话')),
                ('depart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Depart', verbose_name='部门')),
                ('roles', models.ManyToManyField(to='rbac.Role', verbose_name='用户角色')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.School', verbose_name='校区')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]