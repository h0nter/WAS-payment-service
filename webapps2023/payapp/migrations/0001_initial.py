# Generated by Django 4.1.7 on 2023-04-28 09:54

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(choices=[('GBP', 'GBP (British Pound Sterling)'), ('USD', 'USD (United States Dollar)'), ('EUR', 'EUR (Euro)')], default='GBP', max_length=3)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='BalanceTransfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_email', models.EmailField(max_length=254, verbose_name='sender email')),
                ('recipient_email', models.EmailField(max_length=254, verbose_name='recipient email')),
                ('currency', models.CharField(choices=[('GBP', 'GBP (British Pound Sterling)'), ('USD', 'USD (United States Dollar)'), ('EUR', 'EUR (Euro)')], default='GBP', max_length=3)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('description', models.CharField(default='', max_length=50)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Transfer',
                'verbose_name_plural': 'Transfers',
            },
        ),
        migrations.CreateModel(
            name='PaymentRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_email', models.EmailField(max_length=254, verbose_name='sender email')),
                ('recipient_email', models.EmailField(max_length=254, verbose_name='recipient email')),
                ('currency', models.CharField(choices=[('GBP', 'GBP (British Pound Sterling)'), ('USD', 'USD (United States Dollar)'), ('EUR', 'EUR (Euro)')], default='GBP', max_length=3)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('description', models.CharField(default='', max_length=50)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('PND', 'Pending'), ('ACC', 'Accepted'), ('DEC', 'Declined')], default='PND', max_length=3)),
                ('closed_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('REC', 'Transfer received'), ('SND', 'Transferred'), ('REQ', 'Request received'), ('RQU', 'Request update')], default='', max_length=3)),
                ('viewed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payapp.paymentrequest')),
                ('transfer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payapp.balancetransfer')),
            ],
        ),
    ]
