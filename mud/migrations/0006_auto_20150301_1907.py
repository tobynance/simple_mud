# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mud', '0005_auto_20150301_1841'),
    ]

    operations = [
        migrations.RenameField(
            model_name='enemyloot',
            old_name='percent_change',
            new_name='percent_chance',
        ),
    ]
