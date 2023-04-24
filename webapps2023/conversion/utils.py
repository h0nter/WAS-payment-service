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
