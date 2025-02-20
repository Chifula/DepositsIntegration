from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password


class MyAbstractUserManager(BaseUserManager):
    use_in_migrations = True

    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, username, password=None):
        """
        Create and save a User with the given email and password.
        """
        if not username:
            raise ValueError('The Username must be set')

        user = self.model(username=username)
        hashed_password = make_password(password)
        user.set_password(hashed_password)
        user.save()
        return user

    def create_superuser(self, username, password=None):
        """
        Create and save a SuperUser with the given email and password.
        """
        user = self.create_user(username,password=password)
        user.is_staff=True
        user.is_superuser = True
        user.is_active = True
        user.is_admin = True
        user.save(using = self.db)
        return user
