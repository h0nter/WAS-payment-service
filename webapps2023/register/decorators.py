from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .management.user_groups import UserGroups


def check_user_is_in_group(*groups: UserGroups):

    def decorator(function):
        def wrapper(request, *args, **kwargs):
            if request.user.groups.filter(name__in=groups).exists():
                return function(request, *args, **kwargs)
            return HttpResponseForbidden()

        return wrapper

    return decorator


def check_is_customer_admin_redirect(function):
    '''
    Checks if the user is in the CUSTOMERS group,
    if not and they're an admin, redirects to the admin index
    '''
    def wrapper(request, *args, **kwargs):
        # Check if the user is a Customer and return the view
        print(f'User groups {request.user.groups.filter}')
        if request.user.groups.filter(name=UserGroups.CUSTOMERS).exists():
            return function(request, *args, **kwargs)
        # Check if they're an admin and redirect to the admin homepage
        elif request.user.is_admin:
            return HttpResponseRedirect(reverse('admin:index'))

        # In any other case - return a 403
        return HttpResponseForbidden()

    return wrapper
