# Generated by Django 4.0.1 on 2022-02-03 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_alter_profile_storage_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='keydir',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='profile',
            name='bucket_name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='storage_limit',
            field=models.IntegerField(default=5),
        ),
    ]