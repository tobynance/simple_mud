# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mud', '0009_auto_20150301_2038'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='enemy',
            options={'verbose_name_plural': 'Enemies'},
        ),
        migrations.AddField(
            model_name='enemy',
            name='room',
            field=models.ForeignKey(default=1, to='mud.Room'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='player',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=1, to='mud.Room'),
            preserve_default=False,
        ),
    ]
