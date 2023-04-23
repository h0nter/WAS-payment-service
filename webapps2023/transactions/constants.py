from django.db.models import TextChoices


class Currency(TextChoices):
    GBP = 'GBP', 'GBP (British Pound Sterling)'
    USD = 'USD', 'USD (United States Dollar)'
    EUR = 'EUR', 'EUR (Euro)'
