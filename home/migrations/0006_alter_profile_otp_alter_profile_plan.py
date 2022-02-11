# Generated by Django 4.0.1 on 2022-01-30 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_remove_profile_storage_profile_is_payment_done_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='otp',
            field=models.CharField(default='000000', max_length=6),
        ),
        migrations.AlterField(
            model_name='profile',
            name='plan',
            field=models.CharField(choices=[('Free', 'Free'), ('Basic', 'Basic'), ('Premium', 'Premium')], default='free', max_length=10),
        ),
    ]
