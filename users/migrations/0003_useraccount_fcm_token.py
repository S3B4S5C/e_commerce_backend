# Generated by Django 4.2.20 on 2025-04-27 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='fcm_token',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
