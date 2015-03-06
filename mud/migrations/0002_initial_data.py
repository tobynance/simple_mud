# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from mud.import_initial_data import load_fixtures, unload_fixtures


class Migration(migrations.Migration):

    dependencies = [
        ('mud', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixtures, reverse_code=unload_fixtures)
    ]
