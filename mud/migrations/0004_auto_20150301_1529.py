# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management import call_command
from django.db import models, migrations

fixture = "initial_items.json"


########################################################################
def load_fixture(apps, schema_editor):
    call_command('loaddata', fixture, app_label='mud')


########################################################################
def unload_fixture(apps, schema_editor):
    "Brutally deleting all entries for this model..."
    MyModel = apps.get_model("mud", "Item")
    MyModel.objects.all().delete()


########################################################################
class Migration(migrations.Migration):

    dependencies = [
        ('mud', '0003_auto_20150301_1529'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture)
    ]
