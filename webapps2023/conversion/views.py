from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .serializers import ConversionSerializer
from .constants import ConversionRates
from transactions.constants import Currency


class ConversionView(APIView):
    def get(self, request, currency1, currency2, amount_of_currency1, format=None):
        serializer = ConversionSerializer(data)
        return Response(serializer.data)


@api_view(['GET'])
def conversion_rate_and_amount(request, currency1=Currency.GBP, currency2=Currency.USD, amount_of_currency1=0):
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

    if not error_details:
        return Response(data=error_details,
                        status=status.HTTP_400_BAD_REQUEST)

    conversion_rate = 0
    converted_amount = 0

    match [currency1, currency2]:
        case [Currency.GBP, Currency.USD]:
            conversion_rate = ConversionRates.GBP2USD.value
            converted_amount = amount_of_currency1 * conversion_rate
        case [Currency.GBP, Currency.EUR]:
            conversion_rate = ConversionRates.GBP2EUR.value
            converted_amount = amount_of_currency1 * conversion_rate
        case [Currency.USD, Currency.GBP]:
            conversion_rate = ConversionRates.USD2GBP.value
            converted_amount = amount_of_currency1 * conversion_rate
        case [Currency.USD, Currency.EUR]:
            conversion_rate = ConversionRates.USD2EUR.value
            converted_amount = amount_of_currency1 * conversion_rate
        case [Currency.EUR, Currency.GBP]:
            conversion_rate = ConversionRates.EUR2GBP.value
            converted_amount = amount_of_currency1 * conversion_rate
        case [Currency.EUR, Currency.USD]:
            conversion_rate = ConversionRates.EUR2USD.value
            converted_amount = amount_of_currency1 * conversion_rate

    # Build the return data object
    data = {"conversion_rate": conversion_rate, "converted_amount": converted_amount}