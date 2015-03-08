# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Enemy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hit_points', models.SmallIntegerField()),
                ('next_attack_time', models.SmallIntegerField(default=1)),
            ],
            options={
                'verbose_name_plural': 'Enemies',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnemyLoot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percent_chance', models.SmallIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnemyTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=60, db_index=True)),
                ('hit_points', models.SmallIntegerField()),
                ('accuracy', models.SmallIntegerField(default=0)),
                ('dodging', models.SmallIntegerField(default=0)),
                ('strike_damage', models.SmallIntegerField(default=0)),
                ('damage_absorb', models.SmallIntegerField(default=0)),
                ('experience', models.SmallIntegerField()),
                ('money_min', models.SmallIntegerField(default=0)),
                ('money_max', models.SmallIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=60, db_index=True)),
                ('type', models.PositiveSmallIntegerField(default=1, choices=[(0, b'WEAPON'), (1, b'ARMOR'), (2, b'HEALING')])),
                ('min', models.PositiveSmallIntegerField(default=0)),
                ('max', models.PositiveSmallIntegerField(default=0)),
                ('speed', models.PositiveSmallIntegerField(default=0)),
                ('price', models.PositiveIntegerField(default=0)),
                ('strength', models.SmallIntegerField(default=0)),
                ('health', models.SmallIntegerField(default=0)),
                ('agility', models.SmallIntegerField(default=0)),
                ('max_hit_points', models.SmallIntegerField(default=0)),
                ('accuracy', models.SmallIntegerField(default=0)),
                ('dodging', models.SmallIntegerField(default=0)),
                ('strike_damage', models.SmallIntegerField(default=0)),
                ('damage_absorb', models.SmallIntegerField(default=0)),
                ('hp_regen', models.SmallIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_command', models.CharField(default=b'look', max_length=60)),
                ('name', models.CharField(unique=True, max_length=60, db_index=True)),
                ('stat_points', models.PositiveIntegerField(default=18)),
                ('experience', models.PositiveIntegerField(default=0)),
                ('level', models.PositiveSmallIntegerField(default=1)),
                ('money', models.PositiveIntegerField(default=0)),
                ('next_attack_time', models.PositiveIntegerField(default=0)),
                ('hit_points', models.PositiveIntegerField(default=10)),
                ('logged_in', models.BooleanField(default=False, db_index=True)),
                ('active', models.BooleanField(default=False, db_index=True)),
                ('newbie', models.BooleanField(default=True)),
                ('handler', models.PositiveSmallIntegerField(default=0, choices=[(0, b'TRAINING_HANDLER'), (1, b'GAME_HANDLER')])),
                ('base_strength', models.SmallIntegerField(default=1)),
                ('base_health', models.SmallIntegerField(default=1)),
                ('base_agility', models.SmallIntegerField(default=1)),
                ('base_max_hit_points', models.SmallIntegerField(default=0)),
                ('base_accuracy', models.SmallIntegerField(default=0)),
                ('base_dodging', models.SmallIntegerField(default=0)),
                ('base_strike_damage', models.SmallIntegerField(default=0)),
                ('base_damage_absorb', models.SmallIntegerField(default=0)),
                ('base_hp_regen', models.SmallIntegerField(default=0)),
                ('modifier_strength', models.SmallIntegerField(default=0)),
                ('modifier_health', models.SmallIntegerField(default=0)),
                ('modifier_agility', models.SmallIntegerField(default=0)),
                ('modifier_max_hit_points', models.SmallIntegerField(default=0)),
                ('modifier_accuracy', models.SmallIntegerField(default=0)),
                ('modifier_dodging', models.SmallIntegerField(default=0)),
                ('modifier_strike_damage', models.SmallIntegerField(default=0)),
                ('modifier_damage_absorb', models.SmallIntegerField(default=0)),
                ('modifier_hp_regen', models.SmallIntegerField(default=0)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('armor', models.ForeignKey(related_name='+', default=None, blank=True, to='mud.Item', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlayerItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveSmallIntegerField(default=1)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('item', models.ForeignKey(to='mud.Item')),
                ('player', models.ForeignKey(to='mud.Player')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlayerMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('player', models.ForeignKey(to='mud.Player')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60, db_index=True)),
                ('type', models.PositiveSmallIntegerField(default=0, choices=[(0, b'WEAPON'), (1, b'ARMOR'), (2, b'HEALING')])),
                ('description', models.TextField()),
                ('max_enemies', models.PositiveSmallIntegerField(default=0)),
                ('money', models.PositiveIntegerField(default=0)),
                ('east', models.ForeignKey(related_name='+', default=None, to='mud.Room', null=True)),
                ('enemy_type', models.ForeignKey(default=None, to='mud.EnemyTemplate', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoomItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveSmallIntegerField(default=1)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('item', models.ForeignKey(to='mud.Item')),
                ('room', models.ForeignKey(to='mud.Room')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('room', models.ForeignKey(to='mud.Room', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoreItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item', models.ForeignKey(to='mud.Item', on_delete=django.db.models.deletion.PROTECT)),
                ('store', models.ForeignKey(to='mud.Store', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='storeitem',
            unique_together=set([('store', 'item')]),
        ),
        migrations.AddField(
            model_name='room',
            name='items',
            field=models.ManyToManyField(to='mud.Item', through='mud.RoomItem', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='room',
            name='north',
            field=models.ForeignKey(related_name='+', default=None, to='mud.Room', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='room',
            name='south',
            field=models.ForeignKey(related_name='+', default=None, to='mud.Room', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='room',
            name='west',
            field=models.ForeignKey(related_name='+', default=None, to='mud.Room', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='player',
            name='inventory',
            field=models.ManyToManyField(to='mud.Item', through='mud.PlayerItem', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='player',
            name='room',
            field=models.ForeignKey(to='mud.Room', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='player',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='player',
            name='weapon',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='mud.Item', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='enemytemplate',
            name='loot',
            field=models.ManyToManyField(to='mud.Item', through='mud.EnemyLoot', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='enemytemplate',
            name='weapon',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='mud.Item', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='enemyloot',
            name='enemy_template',
            field=models.ForeignKey(to='mud.EnemyTemplate', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='enemyloot',
            name='item',
            field=models.ForeignKey(to='mud.Item', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='enemyloot',
            unique_together=set([('enemy_template', 'item')]),
        ),
        migrations.AddField(
            model_name='enemy',
            name='room',
            field=models.ForeignKey(to='mud.Room'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='enemy',
            name='template',
            field=models.ForeignKey(to='mud.EnemyTemplate', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
    ]
