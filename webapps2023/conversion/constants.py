from enum import Enum


class Currency(Enum):
    GBP = 'GBP'
    USD = 'USD'
    EUR = 'EUR'


class ConversionRate(Enum):
    GBP2USD = 1.20
    GBP2EUR = 1.13
    USD2GBP = 0.80
    USD2EUR = 0.90
    EUR2GBP = 0.89
    EUR2USD = 1.11
