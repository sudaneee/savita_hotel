# Generated by Django 5.1.5 on 2025-01-28 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guest',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='guest',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
