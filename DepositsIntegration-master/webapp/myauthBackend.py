from django.contrib.auth.backends import ModelBackend
from .models import Users


class UserAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Users.objects.get(username=username)
            if user and user.role == '002':
                return user
            if user.role != '002' and user.check_password(raw_password=password):
                return user
            if user.is_superuser or user.is_staff and user.check_password(raw_password=password):
                return user
        except Users.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Users.objects.get(pk=user_id)
        except Users.DoesNotExist:
            return None
