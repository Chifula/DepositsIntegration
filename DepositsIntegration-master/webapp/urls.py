from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib import admin

from . import views


app_name = 'webapp'

urlpatterns = [
    path('', views.UserLogin, name='login'),
    path('history/',views.transaction_history, name='transaction-history'),
    path('account_number/',views.checkAccNumber,name='check-account-number'),
    path('bank_details/upload/verify_account/zicb/',views.zicb_customer_account_number_check),
    path('bank_details/upload/verify_account/other/', views.other_bank_account_number_check),
    path('enter_otp/',views.enterOTP, name = 'enter-otp'),
    path('forgot_password',views.forgotPassword, name = 'forgot-password'),
    path('role/', views.checkUserRole),
    path('account_details/', views.vendor_account_details),
    path('dashboard',views.homepage, name='homepage'),
    path('bank_details/edit/<str:acc_id>/',views.editBankUploadViaForm,name='edit-bank-details'),
    path('bank_details/upload/',views.bankUploadViaForm, name='upload-bank-details'),
    path('bank_details/template/',views.bankUploadCSVTemplate,name='bank-details-template'),
    path('bank_details/upload/csv/',views.bankUploadCSV, name='upload-bank-details-csv'),
    path('bank_details',views.vendorBankDetails,name='bank-details'),
    path('bank_details/search/',views.searchvendorBankDetails,name='search-vendor-bank-details'),
    path('search/', views.get_search_results, name='search-transactions'),
    path('post-transactions/', views.post_transactions, name='post-transactions'),
    path('logout',views.UserLogout, name='logout'),
    path('search-invoices/', views.search_invoice_id, name='search-invoices'),
    path('bank_details/upload/loadBanks/',views.loadBankList),
    path('bank_details/delete/<str:acc_no>/', views.delete_vendor, name='delete'),

]