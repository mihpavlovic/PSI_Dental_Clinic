# Generated by Django 4.2 on 2023-05-28 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osmeh', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordinacija',
            name='centrala',
            field=models.BooleanField(db_column='Centrala', default=0),
        ),
    ]