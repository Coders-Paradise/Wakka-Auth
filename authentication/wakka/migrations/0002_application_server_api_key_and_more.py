# Generated by Django 5.0.2 on 2024-03-13 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wakka', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='server_api_key',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='application',
            name='server_api_key_hash',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
