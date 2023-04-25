import requests
from decimal import Decimal
from django.urls import reverse
import transactions.constants as constants
from .models import Notification


def convert_currency(currency1: constants.Currency, currency2: constants.Currency, amount_in_currency1):
    '''
    Converts the amount in currency1 to currency2 using the conversion API
    :param currency1: The original currency the amount is in.
    :param currency2: The target currency to obtain the new amount for.
    :param amount_in_currency1: The amount to convert.
    :return: the amount in currency2 as a Decimal. If currencies are the same, returns the original amount
    '''
    if currency1 == currency2:
        return Decimal(amount_in_currency1), True

    req_url = f'{constants.CONVERSION_API_URL}{currency1}/{currency2}/{amount_in_currency1}'

    converter_response = requests.get(req_url, verify='certificates/localhost.crt')

    # Check if the conversion API request was successful
    if converter_response.status_code == 200:
        # If it was, unpack the message
        converter_json = converter_response.json()
    else:
        # Otherwise, there was a problem with the conversion, abort the transaction
        return Decimal(-1.0), False

    return Decimal(converter_json['converted_amount']), True


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
