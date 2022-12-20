# Generated by Django 4.1.3 on 2022-12-09 12:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('card', '0007_alter_video_file_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='duration_max',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
        migrations.AddField(
            model_name='card',
            name='duration_min',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
    ]
