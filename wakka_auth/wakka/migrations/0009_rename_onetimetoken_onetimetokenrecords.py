# Generated by Django 5.0.2 on 2024-03-16 02:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wakka', '0008_onetimetoken'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OnetimeToken',
            new_name='OnetimeTokenRecords',
        ),
    ]