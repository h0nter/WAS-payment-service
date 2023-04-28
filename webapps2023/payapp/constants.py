from django.db.models import TextChoices
from decimal import Decimal

# Currency conversion API URL
CONVERSION_API_URL = 'https://localhost:8000/conversion/'

# Used for defining max_digits value of balance/amount fields
MAX_DIGITS = 10


def generate_max_decimal(digits, decimal_places):
    '''
    Generates the maximum value number of digits size, with the set number of decimal places
    :param digits: size of the number in digits
    :param decimal_places: number of decimal places
    :return: Decimal value representing the max number
    '''
    # calculate the maximum possible value for the given number of digits, subtract one digit for the decimal place
    max_value = 10 ** (digits - 1) - 1
    return Decimal(max_value) / Decimal(
        10 ** decimal_places)  # return the maximum value as a decimal number with 2 decimal places


# Used for checking if a user didn't exceed the maximum allowed amount
MAX_AMOUNT = generate_max_decimal(MAX_DIGITS, 2)


class Currency(TextChoices):
    GBP = 'GBP', 'GBP (British Pound Sterling)'
    USD = 'USD', 'USD (United States Dollar)'
    EUR = 'EUR', 'EUR (Euro)'


class RequestStatus(TextChoices):
    PND = 'PND', 'Pending'
    ACC = 'ACC', 'Accepted'
    DEC = 'DEC', 'Declined'


class NotificationType(TextChoices):
    REC = 'REC', 'Transfer received'
    SND = 'SND', 'Transferred'
    REQ = 'REQ', 'Request received'
    RQU = 'RQU', 'Request update'
