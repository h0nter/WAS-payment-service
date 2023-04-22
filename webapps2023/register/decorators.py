from django.http import Http404
from .management.user_groups import UserGroups


def check_user_is_in_group(*groups: UserGroups):

    def decorator(function):
        def wrapper(request, *args, **kwargs):
            if request.user.groups.filter(name__in=groups).exists():
                return function(request, *args, **kwargs)
            raise Http404

        return wrapper

    return decorator
