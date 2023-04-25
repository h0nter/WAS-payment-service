from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ConversionSerializer
from .constants import ConversionRate
from .constants import Currency


@api_view(['GET'])
def conversion_rate_and_amount(request, currency1=Currency.GBP, currency2=Currency.USD, amount_of_currency1=0.0):
    '''
    Provide the conversion rate of currency1 to currency2, and amount_of_currency1 converted into currency2
    '''

    # Validate the currency data, amount is validated by the url (to an extent)
    error_details = {}

    currency_map = Currency._value2member_map_

    if currency1 not in currency_map:
        error_details['currency1'] = [f'A valid currency in: {currency_map} is required']

    if currency2 not in currency_map:
        error_details['currency2'] = [f'A valid currency in: {currency_map} is required']

    if error_details.__len__() != 0:
        return Response(data=error_details,
                        status=status.HTTP_400_BAD_REQUEST)

    # Parse the amount to float for conversion
    amount_of_currency1 = float(amount_of_currency1)

    # Get the conversion rate and convert the amount
    conversion_rate = 0
    converted_amount = 0

    match [Currency(currency1), Currency(currency2)]:
        case [Currency.GBP, Currency.USD]:
            conversion_rate = ConversionRate.GBP2USD.value
            converted_amount = amount_of_currency1 * conversion_rate
        case [Currency.GBP, Currency.EUR]:
            conversion_rate = ConversionRate.GBP2EUR.value
            converted_amount = amount_of_currency1 * conversion_rate
        case [Currency.USD, Currency.GBP]:
            conversion_rate = ConversionRate.USD2GBP.value
            converted_amount = amount_of_currency1 * conversion_rate
        case [Currency.USD, Currency.EUR]:
            conversion_rate = ConversionRate.USD2EUR.value
            converted_amount = amount_of_currency1 * conversion_rate
        case [Currency.EUR, Currency.GBP]:
            conversion_rate = ConversionRate.EUR2GBP.value
            converted_amount = amount_of_currency1 * conversion_rate
        case [Currency.EUR, Currency.USD]:
            conversion_rate = ConversionRate.EUR2USD.value
            converted_amount = amount_of_currency1 * conversion_rate

    # Round the amount to 2dp
    converted_amount = round(converted_amount, 2)

    # Build the return data object
    data = {"conversion_rate": conversion_rate, "converted_amount": converted_amount}

    serializer = ConversionSerializer(data=data)

    if serializer.is_valid():
        return Response(serializer.data)
    else:
        return Response(serializer.errors,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
