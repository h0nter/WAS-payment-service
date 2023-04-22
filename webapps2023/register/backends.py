from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied


class CustomerLoginBackend(ModelBackend):
    '''
    Only allows members of the Customers group to log in through this backend
    '''
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user and user.is_staff:
            # This text won't come up on the login page for security reasons,
            # we don't want people finding out admin usernames/passwords
            raise PermissionDenied('Administrators can only login via the designated admin login page.')
        return user

class AdminLoginBackend(ModelBackend):
    '''
    Only allows administrators to log in through this backend
    '''
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user and not user.is_staff:
            # This text won't come up on the login page for security reasons,
            # we don't want people finding out admin usernames/passwords
            raise PermissionDenied('Customers can only login via the default login panel.')
        return user
