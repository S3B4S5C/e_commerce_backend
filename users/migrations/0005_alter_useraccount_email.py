# Generated by Django 5.2 on 2025-04-17 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_useraccount_is_active_useraccount_is_staff_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
