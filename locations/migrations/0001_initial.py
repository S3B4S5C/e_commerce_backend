# Generated by Django 5.2 on 2025-04-14 01:56

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('country', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('street', models.CharField(max_length=255)),
                ('reference', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Coordinate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('lat', models.DecimalField(decimal_places=6, max_digits=9)),
                ('lon', models.DecimalField(decimal_places=6, max_digits=9)),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='locations.address')),
            ],
        ),
        migrations.AddField(
            model_name='address',
            name='coordinate',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='locations.coordinate'),
        ),
        migrations.CreateModel(
            name='AddressUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='locations.address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.useraccount')),
            ],
            options={
                'unique_together': {('user', 'address')},
            },
        ),
    ]
