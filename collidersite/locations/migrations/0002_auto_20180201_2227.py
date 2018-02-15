# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-01 22:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='locationpage',
            old_name='address',
            new_name='city',
        ),
        migrations.AddField(
            model_name='locationpage',
            name='country',
            field=models.TextField(default='Warsaw'),
            preserve_default=False,
        ),
    ]
