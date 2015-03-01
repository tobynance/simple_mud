# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mud', '0010_auto_20150301_2049'),
    ]

    operations = [
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
        migrations.AddField(
            model_name='storeitem',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=1, to='mud.Store'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='storeitem',
            unique_together=set([('store', 'item')]),
        ),
        migrations.RemoveField(
            model_name='storeitem',
            name='room',
        ),
    ]
