# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mud', '0004_auto_20150301_1529'),
    ]

    operations = [
        migrations.CreateModel(
            name='Enemy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hit_points', models.SmallIntegerField()),
                ('next_attack_time', models.SmallIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnemyLoot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percent_change', models.SmallIntegerField()),
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
                ('loot', models.ManyToManyField(to='mud.Item', through='mud.EnemyLoot')),
                ('weapon', models.ForeignKey(related_name='+', default=None, blank=True, to='mud.Item', null=True)),
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
                ('money', models.PositiveIntegerField(default=0)),
                ('east', models.ForeignKey(related_name='+', default=None, to='mud.Room', null=True)),
                ('enemy_type', models.ForeignKey(default=None, to='mud.EnemyTemplate', null=True)),
                ('items', models.ManyToManyField(to='mud.Item')),
                ('north', models.ForeignKey(related_name='+', default=None, to='mud.Room', null=True)),
                ('south', models.ForeignKey(related_name='+', default=None, to='mud.Room', null=True)),
                ('west', models.ForeignKey(related_name='+', default=None, to='mud.Room', null=True)),
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
                ('room', models.ForeignKey(to='mud.Room', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='storeitem',
            unique_together=set([('room', 'item')]),
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
            name='template',
            field=models.ForeignKey(to='mud.EnemyTemplate', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.CharField(unique=True, max_length=60, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='player',
            name='armor',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='mud.Item', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='player',
            name='name',
            field=models.CharField(unique=True, max_length=60, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='player',
            name='weapon',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='mud.Item', null=True),
            preserve_default=True,
        ),
    ]
