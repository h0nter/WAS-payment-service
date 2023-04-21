from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseNotAllowed
from .forms import CustomUserCreationForm
from .models import Balance, Currency


# User registration view
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

        messages.success(request, 'Registered Successfully!')
        return render(request, 'register/success.html')
    elif request.POST:
        messages.error(request, 'Registration Unsuccessful. Invalid information.')

    return render(request, 'register/sign_up.html', context={'form':form})


# Account overview/Dashboard view
@login_required
def user_dashboard(request):
    # Make sure that only 'GET' requests are allowed to the dashboard
    if request.method == 'GET':
        user = request.user
        return render(request, 'register/dashboard.html', context={'user': user})
    else:
        return HttpResponseNotAllowed(['GET'])

