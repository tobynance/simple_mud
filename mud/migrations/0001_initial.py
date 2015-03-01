# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attributes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('STRENGTH', models.PositiveSmallIntegerField(default=1)),
                ('HEALTH', models.PositiveSmallIntegerField(default=1)),
                ('AGILITY', models.PositiveSmallIntegerField(default=1)),
                ('MAX_HIT_POINTS', models.PositiveSmallIntegerField(default=0)),
                ('ACCURACY', models.PositiveSmallIntegerField(default=0)),
                ('DODGING', models.PositiveSmallIntegerField(default=0)),
                ('STRIKE_DAMAGE', models.PositiveSmallIntegerField(default=0)),
                ('DAMAGE_ABSORB', models.PositiveSmallIntegerField(default=0)),
                ('HP_REGEN', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60, db_index=True)),
                ('type', models.PositiveSmallIntegerField(default=1, choices=[(0, b'WEAPON'), (1, b'ARMOR'), (2, b'HEALING')])),
                ('min', models.PositiveSmallIntegerField(default=0)),
                ('max', models.PositiveSmallIntegerField(default=0)),
                ('speed', models.PositiveSmallIntegerField(default=0)),
                ('price', models.PositiveIntegerField(default=0)),
                ('attributes', models.ForeignKey(to='mud.Attributes')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60, db_index=True)),
                ('password', models.CharField(max_length=20)),
                ('rank', models.PositiveSmallIntegerField(default=0, choices=[(0, b'REGULAR'), (1, b'MODERATOR'), (2, b'ADMIN')])),
                ('stat_points', models.PositiveIntegerField(default=18)),
                ('experience', models.PositiveIntegerField(default=0)),
                ('level', models.PositiveSmallIntegerField(default=1)),
                ('money', models.PositiveIntegerField(default=0)),
                ('next_attack_time', models.PositiveIntegerField(default=0)),
                ('hit_points', models.PositiveIntegerField(default=1)),
                ('logged_in', models.BooleanField(default=False, db_index=True)),
                ('active', models.BooleanField(default=False, db_index=True)),
                ('newbie', models.BooleanField(default=True)),
                ('armor', models.ForeignKey(related_name='armor_player', default=None, blank=True, to='mud.Item', null=True)),
                ('base_attributes', models.ForeignKey(to='mud.Attributes')),
                ('weapon', models.ForeignKey(related_name='weapon_player', default=None, blank=True, to='mud.Item', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
