# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-12 23:14
from __future__ import unicode_literals

from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('industries', '0001_initial'),
        ('people', '0007_auto_20180209_2305'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='industries',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, related_name='people_industries', to='industries.IndustryPage'),
        ),
    ]
