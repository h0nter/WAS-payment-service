from django.db import models
from register.models import CustomUser
from .constants import Currency


class Balance(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.GBP)
    amount = models.DecimalField(max_digits=19, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.amount} {self.currency}'


class BalanceTransfer(models.Model):
    sender_email = models.EmailField('sender email', max_length=254)
    recipient_email = models.EmailField('recipient email', max_length=254)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.GBP)
    amount = models.DecimalField(max_digits=19, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.amount} {self.currency} sent, from: {self.sender_email} to: {self.recipient_email}'
