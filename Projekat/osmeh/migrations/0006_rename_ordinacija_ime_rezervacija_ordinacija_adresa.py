# Generated by Django 4.2 on 2023-06-04 13:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('osmeh', '0005_rezervacija_ordinacija_ime_rezervacija_pacijent_ime_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rezervacija',
            old_name='ordinacija_ime',
            new_name='ordinacija_adresa',
        ),
    ]
