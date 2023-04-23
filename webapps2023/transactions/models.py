from django.db import models
from django.utils import timezone
from register.models import CustomUser
import transactions.constants as constants


class Balance(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, choices=constants.Currency.choices, default=constants.Currency.GBP)
    amount = models.DecimalField(max_digits=constants.MAX_DIGITS, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.amount} {self.currency}'


class BalanceTransfer(models.Model):
    sender_email = models.EmailField('sender email', max_length=254)
    recipient_email = models.EmailField('recipient email', max_length=254)
    currency = models.CharField(max_length=3, choices=constants.Currency.choices, default=constants.Currency.GBP)
    amount = models.DecimalField(max_digits=constants.MAX_DIGITS, decimal_places=2, default=0.00)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.amount} {self.currency} sent, ' \
               f'from: {self.sender_email} to: {self.recipient_email},' \
               f' on: {self.date.date()}, at: {self.date.strftime("%H:%M:%S")}'

    class Meta:
        verbose_name = "Transfer"
        verbose_name_plural = "Transfers"
