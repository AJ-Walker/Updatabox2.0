# Generated by Django 4.0.1 on 2022-02-02 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='storage_limit',
            field=models.IntegerField(default='5'),
        ),
    ]
