from django.core.exceptions import PermissionDenied


def user_is_approver(function):
    def wrap(request, *args, **kwargs):

        if request.user.role == '002':
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrap


def user_is_support_staff(function):
    def wrap(request, *args, **kwargs):

        if request.user.role == '001':
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrap
