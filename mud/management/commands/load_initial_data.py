# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management import call_command
from django.core.management.base import BaseCommand


fixtures = ["initial_items.json",
            "initial_enemy_templates.json",
            "initial_rooms.json",
            "initial_stores.json",
            "initial_users.json"]


########################################################################
class Command(BaseCommand):
    help = 'load the initial game data'

    ####################################################################
    def handle(self, *args, **options):
        for fixture in fixtures:
            call_command('loaddata', fixture, app_label='mud')
