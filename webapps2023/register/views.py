from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.urls import reverse
from django.forms import ValidationError
from .forms import CustomUserCreationForm
from .models import Balance, Currency
from .decorators import check_is_customer_admin_redirect
from .management.user_groups import UserGroups


# User login
class CustomLoginView(LoginView):
    template_name = 'register/login.html'
    redirect_authenticated_user = True


# Admin Login
class CustomLoginViewAdmin(LoginView):
    template_name = 'register/admin_login.html'

    # Users' authenticated - need to log them in
    def form_valid(self, form):
        user = form.get_user()

        if user is not None:
            # Check if the user has activated their account (admin accounts are active by default)
            if user.is_active:

                request = form.request

                # Log the user in
                login(request, user)

                # Check if the user needs to change their password, because
                # - they're an admin, and it's their first time logging in
                if user.change_password:
                    return HttpResponseRedirect(reverse('admin:password_change'))

                # Redirect the user to the next page
                if 'next' in request.POST:
                    return HttpResponseRedirect(reverse(request.POST.get('next')))
                else:
                    return HttpResponseRedirect(reverse('admin:index'))
            else:
                # Return a 'disabled account' error message
                return ValidationError("You need to activate your account before logging in.")

        return ValidationError("There was a problem logging you in, please try again.")


class CustomPasswordChangeViewAdmin(PasswordChangeView):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        print(kwargs['user'])
        return kwargs

    def form_valid(self, form):
        user = form.user
        if not user is None:
            # Change the flag, so user isn't prompted to change the password again next time
            user.change_password = False
            user.save()
        return super().form_valid(form)


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
@check_is_customer_admin_redirect
def user_dashboard(request):
    # Make sure that only 'GET' requests are allowed to the dashboard
    if request.method == 'GET':
        user = request.user
        return render(request, 'register/dashboard.html', context={'user': user})
    else:
        return HttpResponseNotAllowed(['GET'])

