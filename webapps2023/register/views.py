from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.views import LoginView, PasswordChangeView, TemplateView
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.urls import reverse
from django.forms import ValidationError
from django.conf import settings
from django.core.exceptions import PermissionDenied
from .forms import CustomUserCreationForm
from payapp.models import Balance
from payapp.utils import get_notifications
from .management.user_groups import UserGroups
from .decorators import check_user_is_in_group, allow_customer_redirect_admin, redirect_if_logged_in


@method_decorator([redirect_if_logged_in], name='dispatch')
class CustomTemplateView(TemplateView):
    # Add user to the template context for navigation bar set-up
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


@method_decorator([redirect_if_logged_in, csrf_protect], name='dispatch')
# User login
class CustomLoginView(LoginView):
    template_name = 'register/login.html'
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        # Set the AUTHENTICATION_BACKENDS setting to the custom backend
        settings.AUTHENTICATION_BACKENDS = ['register.backends.CustomerLoginBackend']

        try:
            # Call the parent dispatch method to handle the login
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            # Handle the PermissionDenied exception if the user is an admin
            return self.handle_no_permission()


@method_decorator([redirect_if_logged_in, csrf_protect], name='dispatch')
# Admin Login
class CustomLoginViewAdmin(LoginView):
    template_name = 'register/admin_login.html'
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        # Set the AUTHENTICATION_BACKENDS setting to the custom backend
        settings.AUTHENTICATION_BACKENDS = ['register.backends.AdminLoginBackend']

        try:
            # Call the parent dispatch method to handle the login
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            # Handle the PermissionDenied exception if the user is a customer
            return self.handle_no_permission()

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


@method_decorator([check_user_is_in_group(UserGroups.ADMINS), csrf_protect], name='dispatch')
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


@redirect_if_logged_in
@csrf_protect
# User registration view
def sign_up(request):
    form = CustomUserCreationForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, 'Registered Successfully!')
        return render(request, 'register/success.html')
    elif request.POST:
        messages.error(request, 'Registration Unsuccessful. Invalid information.')

    return render(request, 'register/sign_up.html', context={'form': form})


# Account overview/Dashboard view
@login_required
@allow_customer_redirect_admin
def user_dashboard(request):
    # Render the dashboard
    user = request.user
    balance = Balance.objects.get(user=user)
    return render(request, 'register/dashboard.html',
                  context={'user': user, "notifications": get_notifications(user), 'balance': balance})
