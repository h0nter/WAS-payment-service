from math import ceil
from .constants import Currency
from decimal import Decimal


def convert_currency(base_currency: Currency, target_currency: Currency, amount: Decimal):
    '''
    Converts the amount in base_currency to target_currency
    :param base_currency: The original currency the amount is in.
    :param target_currency: The target currency to obtain the new amount for.
    :param amount: The amount in base_currency to convert.
    :return: the amount in target_currency as a float. If currencies are the same, returns the original amount
    '''

    amount = float(amount)

    if base_currency != target_currency:

        # Get the conversion rates
        gbp2usd = 1.20
        gbp2eur = 1.13
        usd2gbp = 0.80
        usd2eur = 0.90
        eur2gbp = 0.89
        eur2usd = 1.11

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

    return amount


def round_up_2dp(number: float):
    '''
    Rounds the given number up to the nearest 2 decimal places
    :param number: a float to round up
    :return: the float rounded up to 2 d.p.
    '''
    return (ceil(number * 100)) / 100
