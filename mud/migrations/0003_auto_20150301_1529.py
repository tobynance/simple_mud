# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mud', '0002_auto_20150301_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='AGILITY',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='HEALTH',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='STRENGTH',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
