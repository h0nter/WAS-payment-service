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
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.amount} {self.currency} sent, ' \
               f'from: {self.sender_email} to: {self.recipient_email},' \
               f' on: {self.date.date()}, at: {self.date.strftime("%H:%M:%S")}'

    class Meta:
        verbose_name = "Transfer"
        verbose_name_plural = "Transfers"


class RequestStatus(models.TextChoices):
    PND = 'PND', 'Pending'
    ACC = 'ACC', 'Accepted'
    DEC = 'DEC', 'Declined'


class PaymentRequest(models.Model):
    sender_email = models.EmailField('sender email', max_length=254)
    recipient_email = models.EmailField('recipient email', max_length=254)
    currency = models.CharField(max_length=3, choices=constants.Currency.choices, default=constants.Currency.GBP)
    amount = models.DecimalField(max_digits=constants.MAX_DIGITS, decimal_places=2, default=0.00)
    start_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=3, choices=RequestStatus.choices, default=RequestStatus.PND)
    closed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'User: {self.sender_email} requested {self.amount} {self.currency}, ' \
               f'from: {self.recipient_email}, on: {self.start_date.date()}, ' \
               f'at: {self.start_date.strftime("%H:%M:%S")}, status: {self.status},' \
               f'closed: {self.closed_date}'


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=constants.NotificationType.choices, default='')
    transfer = models.ForeignKey(BalanceTransfer, on_delete=models.CASCADE, null=True, blank=True)
    request = models.ForeignKey(PaymentRequest, on_delete=models.CASCADE, null=True, blank=True)
    viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
