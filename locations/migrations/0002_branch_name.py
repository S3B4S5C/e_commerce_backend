# Generated by Django 4.2.20 on 2025-04-18 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
