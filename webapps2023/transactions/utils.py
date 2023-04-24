from math import ceil
from decimal import Decimal
from django.urls import reverse
import transactions.constants as constants
from .models import Notification


def convert_currency(base_currency: constants.Currency, target_currency: constants.Currency, amount: Decimal):
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
            case [constants.Currency.GBP, constants.Currency.USD]:
                amount = amount * gbp2usd
            case [constants.Currency.GBP, constants.Currency.EUR]:
                amount = amount * gbp2eur
            case [constants.Currency.USD, constants.Currency.GBP]:
                amount = amount * usd2gbp
            case [constants.Currency.USD, constants.Currency.EUR]:
                amount = amount * usd2eur
            case [constants.Currency.EUR, constants.Currency.GBP]:
                amount = amount * eur2gbp
            case [constants.Currency.EUR, constants.Currency.USD]:
                amount = amount * eur2usd

    return amount


def round_up_2dp(number: float):
    '''
    Rounds the given number up to the nearest 2 decimal places
    :param number: a float to round up
    :return: the float rounded up to 2 d.p.
    '''
    return (ceil(number * 100)) / 100


def get_notifications(user):
    '''
    Fetches all notifications for the given user
    :param user: currently logged-in user
    :return: List of dictionaries for rendering notifications in the template
    '''

    # Get the last 10 notifications for the user
    qs = Notification.objects.filter(user=user).order_by('-created_at')[:10]

    # Return list
    notifications = []

    # Unpack each notification into a dictionary
    for n in qs:

        notif_type = constants.NotificationType(n.type)

        amount = 0
        currency = constants.Currency.GBP
        from_to = 'From'
        usr_email = ''
        url = '#'

        match notif_type:
            case constants.NotificationType.REC:
                amount = n.transfer.amount
                currency = n.transfer.currency
                from_to = 'From'
                usr_email = n.transfer.sender_email
                url = reverse('transactions')

            case constants.NotificationType.SND:
                amount = n.transfer.amount
                currency = n.transfer.currency
                from_to = 'To'
                usr_email = n.transfer.recipient_email
                url = reverse('transactions')

            case constants.NotificationType.REQ:
                amount = n.request.amount
                currency = n.request.currency
                from_to = 'From'
                usr_email = n.request.sender_email
                url = reverse('requests_update_status', kwargs={'pk': n.request.id})

            case constants.NotificationType.RQU:
                amount = n.request.amount
                currency = n.request.currency
                from_to = 'To'
                usr_email = n.request.recipient_email
                url = reverse('requests')

        notif = {'date': n.created_at.date(),
                 'type': notif_type.label,
                 'user_email': usr_email,
                 'dir': from_to,
                 'currency': currency,
                 'amount': amount,
                 'url': url}

        notifications.append(notif)

    return notifications
