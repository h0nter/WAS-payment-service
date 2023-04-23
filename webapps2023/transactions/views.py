from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from register.decorators import allow_customer_redirect_admin
from decimal import Decimal
from .models import Balance
from .constants import Currency
from .utils import convert_currency
from .forms import BalanceTransferForm


@login_required
@allow_customer_redirect_admin
def balance_transfer(request):
    if request.method == 'POST':
        form = BalanceTransferForm(request.POST, request=request)

        if form.is_valid():
            sender_user = request.user
            sender_currency = sender_user.currency

            recipient_email = form.cleaned_data.get("recipient_email")
            amount = form.cleaned_data.get("amount")
            src_currency = form.cleaned_data.get('currency')

            inter_amount = convert_currency(src_currency, sender_currency, amount)

            sender_balance = Balance.objects.get(user=sender_user)
            sender_balance.amount = sender_balance.amount - inter_amount
            sender_balance.save()

            recipient_balance = Balance.objects.get(user__email=recipient_email)
            recipient_currency = recipient_balance.currency

            amount = convert_currency(src_currency, recipient_currency, amount)

            recipient_balance.amount = recipient_balance.amount + amount
            recipient_balance.save()

            form.save()

            return render(request, "transactions/transfer_success.html", {"user": request.user})

    else:
        form = BalanceTransferForm(request=request)

    return render(request, "transactions/balance_transfer.html", {"form": form, "user": request.user})
