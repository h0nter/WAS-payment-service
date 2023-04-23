# Generated by Django 4.1.7 on 2023-04-23 00:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BalanceTransfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_email', models.EmailField(max_length=254, verbose_name='sender email')),
                ('recipient_email', models.EmailField(max_length=254, verbose_name='recipient email')),
                ('currency', models.CharField(choices=[('GBP', 'GBP (British Pound Sterling)'), ('USD', 'USD (United States Dollar)'), ('EUR', 'EUR (Euro)')], default='GBP', max_length=3)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=19)),
            ],
        ),
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(choices=[('GBP', 'GBP (British Pound Sterling)'), ('USD', 'USD (United States Dollar)'), ('EUR', 'EUR (Euro)')], default='GBP', max_length=3)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=19)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]