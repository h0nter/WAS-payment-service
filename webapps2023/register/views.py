from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import Balance, Currency


# Create your views here.
def sign_up(request):

    form = CustomUserCreationForm(request.POST or None)

    if form.is_valid():
        user = form.save()

        # Get the conversion rates from GBP
        gbp2usd = 1.20
        gbp2eur = 1.13

        # Assign the user equivalent of 1000 GBP in their selected currency
        amount = 1000

        match user.currency:
            case Currency.USD:
                amount = amount * gbp2usd
            case Currency.EUR:
                amount = amount * gbp2eur

        Balance.objects.create(user=user, currency=user.currency, amount=amount)

        messages.success(request, "Registered Successfully!")
        return render(request, "registration/success.html")
    elif request.POST:
        messages.error(request, "Registration Unsuccessful. Invalid information.")

    return render(request, "registration/sign_up.html", context={"sign_up_form":form})
