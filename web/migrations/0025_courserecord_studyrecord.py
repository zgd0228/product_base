# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2019-04-11 16:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0024_auto_20190412_0008'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_num', models.IntegerField(verbose_name='节次')),
                ('date', models.DateField(auto_now_add=True, verbose_name='上课日期')),
                ('class_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.ClassList', verbose_name='班级')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.UserInfo', verbose_name='讲师')),
            ],
        ),
        migrations.CreateModel(
            name='StudyRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record', models.CharField(choices=[('checked', '已签到'), ('vacate', '请假'), ('late', '迟到'), ('noshow', '缺勤'), ('leave_early', '早退')], default='checked', max_length=64, verbose_name='上课纪录')),
                ('course_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.CourseRecord', verbose_name='第几天课程')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Student', verbose_name='学员')),
            ],
        ),
    ]
