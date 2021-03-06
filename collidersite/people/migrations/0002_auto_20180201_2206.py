# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-01 22:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='peopleindexpage',
            name='introduction',
        ),
        migrations.AddField(
            model_name='peopleindexpage',
            name='introduction_advisors',
            field=models.TextField(blank=True, help_text='Text to describe the advisors'),
        ),
        migrations.AddField(
            model_name='peopleindexpage',
            name='introduction_team',
            field=models.TextField(blank=True, help_text='Text to describe the ic team'),
        ),
        migrations.AddField(
            model_name='person',
            name='covered_markets',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, related_name='covered_markets', to='locations.LocationPage'),
        ),
        migrations.AddField(
            model_name='person',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location', to='locations.LocationPage'),
        ),
    ]
