# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2019-04-08 08:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0013_auto_20190408_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classlist',
            name='memo',
            field=models.TextField(blank=True, verbose_name='说明'),
        ),
    ]