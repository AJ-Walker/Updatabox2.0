# Generated by Django 4.0.1 on 2022-01-31 07:42

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_alter_profile_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='plan_end_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='profile',
            name='plan_start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
