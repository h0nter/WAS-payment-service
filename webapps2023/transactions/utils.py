from .constants import Currency
from decimal import Decimal


def convert_currency(base_currency: Currency, target_currency: Currency, amount: Decimal):
    if base_currency != target_currency:

        # Get the conversion rates
        gbp2usd = 1.20
        gbp2eur = 1.13
        usd2gbp = 0.80
        usd2eur = 0.90
        eur2gbp = 0.89
        eur2usd = 1.11

        amount = float(amount)

        match [base_currency, target_currency]:
            case [Currency.GBP, Currency.USD]:
                amount = amount * gbp2usd
            case [Currency.GBP, Currency.EUR]:
                amount = amount * gbp2eur
            case [Currency.USD, Currency.GBP]:
                amount = amount * usd2gbp
            case [Currency.USD, Currency.EUR]:
                amount = amount * usd2eur
            case [Currency.EUR, Currency.GBP]:
                amount = amount * eur2gbp
            case [Currency.EUR, Currency.USD]:
                amount = amount * eur2usd

        amount = Decimal(round(amount, 2))

    return amount
