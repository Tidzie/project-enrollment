# Generated by Django 4.2.7 on 2025-05-20 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='child',
            name='passport_photo',
            field=models.ImageField(blank=True, null=True, upload_to='passport_photos/'),
        ),
    ]
