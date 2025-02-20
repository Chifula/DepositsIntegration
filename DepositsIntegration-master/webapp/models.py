from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from .managers import MyAbstractUserManager



ROLE = (
    ('001', "001"),  # Adds Bank Details
    ('002', "002"),  # Posts Transactions
)


class ApiCallErrors(models.Model):
    service = models.CharField(max_length=255)
    error_list = models.TextField()
    transaction_type = models.CharField(max_length=255)


class Users(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255,blank=True)
    cif = models.CharField(max_length=255)
    role = models.CharField(max_length=255, choices=ROLE)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)
    objects = MyAbstractUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

class UserLoginHistory(models.Model):
    username = models.CharField(max_length=255)
    ipaddress = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now=True)


class BankDetails(models.Model):
    account_no = models.CharField(max_length=20, unique=True, verbose_name='Account Number')
    account_name = models.CharField(max_length=255, verbose_name='Account Name')
    vendor_id = models.CharField(max_length=255, verbose_name='Vendor ID')
    vendor_mobile_number = models.CharField(max_length=20, verbose_name='Vendor Mobile Number', blank=True)
    vendor_email = models.EmailField(max_length=255, verbose_name='Vendor Email', blank=True)
    bank_name = models.CharField(max_length=255, verbose_name='Bank Name')
    sort_code = models.CharField(max_length=255, verbose_name='Sort Code')
    branch = models.CharField(max_length=255, verbose_name='Branch Name')
    bicCode = models.CharField(max_length=355,verbose_name='BIC Code',null=True)

class ProcessedDeposits(models.Model):
    invoiceid = models.CharField(max_length=255, blank=False, unique=True)
    vendorid = models.CharField(max_length=255, blank=False,)
    vendorname = models.CharField(max_length=255, blank=False)
    transaction_date = models.CharField(max_length=255, blank=False, unique=False)
    amount = models.CharField(max_length=255, blank=False)
    status = models.IntegerField()
    transaction_type = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now=True)
    processed_by = models.CharField(max_length=255)