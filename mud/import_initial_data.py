# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management import call_command

fixtures = ["initial_items.json",
            "initial_enemy_templates.json",
            "initial_rooms.json",
            "initial_stores.json"]


########################################################################
def load_fixtures(apps, schema_editor):
    for fixture in fixtures:
        call_command('loaddata', fixture, app_label='mud')


########################################################################
def unload_fixtures(apps, schema_editor):
    """Brutally deleting all entries for these models..."""
    for model in ["Item", "EnemyTemplate", "Room", "Store"]:
        MyModel = apps.get_model("mud", model)
        MyModel.objects.all().delete()


# from mud.import_initial_data import load_fixtures, unload_fixtures
#
# class Migration(migrations.Migration):
#
#     dependencies = [
#         ('mud', '0001_initial'),
#     ]
#
#     operations = [
#         migrations.RunPython(load_fixtures, reverse_code=unload_fixtures)
#     ]
