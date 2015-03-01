# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mud', '0007_auto_20150301_1907'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='name',
        ),
        migrations.RemoveField(
            model_name='player',
            name='password',
        ),
        migrations.RemoveField(
            model_name='player',
            name='rank',
        ),
        migrations.AddField(
            model_name='player',
            name='user',
            field=models.OneToOneField(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='room',
            name='max_enemies',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
