# Generated by Django 4.1.7 on 2023-04-23 00:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0003_init_admins'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Balance',
        ),
    ]