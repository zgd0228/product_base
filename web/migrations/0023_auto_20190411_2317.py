# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2019-04-11 15:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0022_auto_20190411_1033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='memo',
            field=models.TextField(blank=True, max_length=255, null=True, verbose_name='备注'),
        ),
    ]