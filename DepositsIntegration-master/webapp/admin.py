from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password

from .models import Users, BankDetails


class CustomUserAdmin(UserAdmin):
    authentication_backends = ['webapp.myauthBackend.UserAuthBackend']
    list_display = ('username', 'password','is_staff','role','cif')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    search_fields = ('username',)
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password', 'role','cif')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', )}),

    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'role','cif', 'password1', 'password2'),
        }),)


admin.site.register(BankDetails)
admin.site.register(Users, CustomUserAdmin)
