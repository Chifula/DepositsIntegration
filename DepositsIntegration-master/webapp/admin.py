from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password

from .models import Users, BankDetails
from .models import TransactionSummary
from .models import PaymentSummary

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

@admin.register(TransactionSummary)
class TransactionSummaryAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'amount', 'status', 'customer_name', 'processed_amount', 'processed_transaction_date')
    list_filter = ('status', 'payment_method')
    search_fields = ('transaction_id', 'customer_name')

@admin.register(PaymentSummary)
class PaymentSummaryAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'amount', 'payment_status', 'customer_name', 'processed_amount', 'transaction_date')
    list_filter = ('payment_status', 'payment_method')
    search_fields = ('transaction_id', 'customer_name')

