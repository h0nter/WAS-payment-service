from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.contrib import messages
from register.decorators import allow_customer_redirect_admin
from decimal import Decimal
from .models import Balance
import transactions.constants as constants
from .utils import convert_currency, round_up_2dp
from .forms import BalanceTransferForm


@login_required
@allow_customer_redirect_admin
def balance_transfer(request):
    if request.method == 'POST':
        form = BalanceTransferForm(request.POST, request=request)

        if form.is_valid():

            # This block makes no connection/changes to the db, if it fails, simply return an error

            # Fetch sender data and calculate the transaction amount to subtract
            sender_user = request.user
            sender_currency = sender_user.currency

            # Fetch the recipient's data
            recipient_email = form.cleaned_data.get("recipient_email")
            recipient_currency = Balance.objects.get(user__email=recipient_email).currency

            # Calculate the amounts to subtract/add in the transaction
            transfer_amount = form.cleaned_data.get("amount")
            transfer_currency = form.cleaned_data.get('currency')

            # Calculate the amount to subtract from the sender's account
            # always round up, as we don't want to end up subtracting less money than is added to the recipient
            # this won't have any effect if the currencies match
            sub_amount = Decimal(round_up_2dp(convert_currency(transfer_currency, sender_currency, transfer_amount)))

            # Calculate the amount to subtract from the sender's account
            # since the money out is rounded up already, we can simply round here
            # this won't have any effect if the currencies match
            add_amount = Decimal(round(convert_currency(transfer_currency, recipient_currency, transfer_amount), 2))

            sender_balance = Balance.objects.select_for_update().get(user=sender_user)
            recipient_balance = Balance.objects.select_for_update().get(user__email=recipient_email)

            # A flag for transaction completed successfully
            success = False

            # Run this block in transaction, so either the whole transfer is completed,
            # or fully rolled back to maintain integrity
            try:
                with transaction.atomic():
                    if sender_balance.amount < sub_amount:
                        raise ValueError('Insufficient funds to complete the transfer.')

                    sender_balance.amount = sender_balance.amount - sub_amount
                    sender_balance.save()

                    if (recipient_balance.amount + add_amount) > constants.MAX_AMOUNT:
                        raise ValueError(
                            'The amounts involved in this transaction exceed our limits. ' +
                            'Please contact our technical support')
                    recipient_balance.amount = recipient_balance.amount + add_amount
                    recipient_balance.save()

                    form.save()
                    success = True

            except IntegrityError:
                # In case the transaction fails at any point, send an error message
                messages.error(request,
                               'We encountered some problems with completing your transfer, please try again later.')
            except ValueError as e:
                messages.error(request, str(e))

            # If transaction was completed, show success message
            if success:
                return render(request, "transactions/transfer_success.html", {"user": request.user})

    else:
        form = BalanceTransferForm(request=request)

    return render(request, "transactions/balance_transfer.html", {"form": form, "user": request.user})
