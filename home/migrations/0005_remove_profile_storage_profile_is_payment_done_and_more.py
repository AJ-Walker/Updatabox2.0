# Generated by Django 4.0.1 on 2022-01-29 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='storage',
        ),
        migrations.AddField(
            model_name='profile',
            name='is_payment_done',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='storage_limit',
            field=models.CharField(default='5GB', max_length=10),
        ),
    ]
