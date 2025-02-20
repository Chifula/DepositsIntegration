import datetime
import io
from itertools import groupby
from operator import attrgetter
from _decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from sqlalchemy import not_
from sqlalchemy.orm import class_mapper

from .forms import BankDetailsForm
from .helpers import *
from .myauthBackend import UserAuthBackend
from .permissions import user_is_approver, user_is_support_staff
from .services import *
from .models import ProcessedDeposits, BankDetails, Users
import requests
import pandas as pd

URL = "https://41.175.13.198:7664/api/json/commercials/zicb/banking"
IFT_KEY = "wmdTRHHpCAqgpCMMBfQUGZzpvOaOWmIFuNElwQBeuyyeRfHlRadnHSbMWimMZfPFhKIQEEgFPjkeJgHRwbTErvAZRlLJrVNhqSQRknxXpZhlsdzAuTTZtPZHFJOsvWtIRreHzFjPSEkwmGNdsOCMYipktXBeMkYEoWwFobzrUJRVJXeBWBveZYqirlbVlcwRXDdRJSIoFUMtxjFcbjFvxEKlmVzdjIpGWrqegWDOZQMOqLwSXsdBYjhkvcbQERolchgYpZbrmYRSMUFIHfiSBESXyVIeUAcXAhIcQAAQjWOVoZhuURxJNKRFUNiSMLOnIDwxaesFAwJPuZHbbKeMDxXzRQWaGCoaqKVjZshMpHVcEcncAZeKiioptRnpLAvmGHlrAXxSkaHgpWaqitRvYGOWDDMIxzsccEHpOfwsAfyZpCJyPRcpwiuCUTRRyOspSpWvFVIrHZxnzSizXkkVZtlhPeSYBrxplbhoAFYAPmxaZkAsNjQphlcfwmaZKzWreSkBpbGKrCcllzDcyibtGnbSlqqFZGIWFpokiyKVmcUaHDitetRwNMdksycsCsGTTiNysYVbeqLPFuGPTdrzfsMZZRQkAHqmyuYOMxQeEvpXibFylxPaoeaTXVWAVozTfdSIuufLgoADbvtDTpvpDhMiMcmPIIICEyeHpjyLGGFwqhBeSkVvYuQLSnHnoMlMZwCKRXzCXVjkcxEYCYflOdImrjPlMYzRNQjaCaMhhpBJTWoRDpQGaIhIQcsVAyHMtYIlRwEhGpnXZTFxshsxyDTBHPxaSKoPuHejMLQYIXyiMLtPfFJfZXYNAXfDXstXEBIHgqvYZAlogYbMPVIkDCceNNuaxkrRTAtcZGESKsRuPGOrukdHkdGaAGsbTSAgLXZmCkowppFOWZjgIJPiySyeeQOIQOfmcEyPWpByRBUxGmCnuOFbmbXEUBuuROdJsCKhfuaGIavHBUBdUuuhwuwEUOXYYwGmTEXXmVXRZrJLsDruGoYpYmTAcciUWMssQQRDEPhhuCEAkUZlfYoNkqUadbgEEzvJTQTkVPbeFnsoCPWKBEYeAqiwYpunQaLiUBpTMEuLGicQRgNnLvxbvJbKLYTxr"
DDAC_KEY = "DdzDsZAhnpCBYdYIjTMGnwLkCdjUSqXKtPNBtnEggTpXMjVFPZRKplbvkxDcXkAdgZaaHMmZWfMvtixnOpjpgLTltGlBsnaUwfsoqXMaFNOudDUAJOCukUnnuEbAgLyqqkevkoOWcrSiUeXkTzHcmiNhoiIcTeTxwgUMvOUxPqXdFVXGjPRKRRRlOtaLibcMYOIPcIVgQwgNuLcbRAEzvIoFyHphPWZxIUmZLWQDLQdjjZNzfuwLyecspNCZKTjIPhbFbHKERezyxEBbUGMuLltbeyDVpxoAGtaWEHyrhpJxVkATMOEwuNHTNfKeioLNeHhwauJWjLnqeNlbrvZYLcYqAxIieOiuqFxKLOIhnFsoXtEZlJoYmUlrCSZPZpAzfGtOCjmHCksctYwepNVXCZEScYnbskmdqHWyZkSNgMzYceRkkbxnbzgmpSiUJpyEWjBNbNZiPbbENkwhKtHAVJKzPJpzrGvLWwPKGUdXkPpMMbZVlNZGeAOcQBLEnHiLSpfcVrpKoIUYBFKvhUNKVXeMmEmQUCpciEtAZwUdfPyKOheYdtQFXbklwppeFEeOVnqQBgHhTCZlNbETHSdSYLihxOjqDeBRsfVzrdTwiSTVvkSJxbBEuuRcbZCYJOOUtyTjcpNEVdKvHJirRLfoSOltxNQFTGMtCJTqnaeEZFSSIbHyjaDVeJyfHilqlpysiDEKRFawquymCzHTSckbQYrHNjdfoMXFUVYYTFExtEHkGjLZAXplCVDMRIJkxBOFqksPddOGfaUMQdEYUGjCNxVdjpYKPcSXDVJGhXRkyikoAiBiKOGipzSJowglSvjUQtqoqBUswPTUxsPTfOIUTpXIrdghCmSjFpKLKWndmuiXpawEjVYbwBDaVdqGoYqNrxfpjkYspZoJrNMpNGPBhlvQMJJtgajNhHyOHtUqhTEPwDaVVuYdWsBmLlWCeEBqpyHPnwkGHJzrDieaSqoYHnpXtosFCIATDeTSZepebGcNbMCAjmfThNvUVoOGXaYOIXCKsUCdqDnpMolNEZUWLJhHFTpahUmUXvvuxtxyepgyhJRjEhDsISFENzkUkFxyKptCdjPePLaLjnXPFweLBUMUIuyBl"
API_KEY = "jVKRmqnoqsmoMXfhgaEjeXKctmtWdMpaPKINOfaiglVaWkVraFYngtYcfspiitZIcKjfZUwPTPHRNUrIgdiAyqpgplQFDJYwDCvzdUnnxalobZxzOCMWVKhVQZYiEfukQUCTeXOhKAIXTWSLszsFmuwZAGwTmpBUTjraYerObIOEAJbmEffhhxRgsglFAPPkKVCIzNkyzCaMxyIuNVdjHURqzqimwoPfkugKrgBNCTOZWYrUVyXKbGaeUayugjUFfbdboEOwipAQxQgTDrfpBGcSVELjqtrqTtlElIShCwUErSqvZVGneqWXEvuRwOqbVtJSbqZyReGCpRyXaivqoDSycUpDYnSymrcwQBDSTZRVIKALobWZxHQpVeTCfEhqDqfMydQqVjRpSaljyIRoIXDkhqhuEsZWVKZmgcbPxvTPSAuCoIvYfjdoFRZVemldnYZctyjTUTtmfiQQPRibOHwVEbstjZacCLHwgXPxtzRtdSypEjJcdkCUnfulNPtlSheLzNgtpAdQjWcuruYNtIgreCZELvbYxxYDlwWIngVmuzLTERviDjwYjeaeVnJxWecdIeLylpLKNHPobrXnJBltzgknhsqdKlKtoRqQobuvoCGVySOoTDPFhzjjeZGscCOvgKecixZdgXrRnghhsCuefYzgiCrHzmAaObiHIKPWxuFJkBaXxhNYOjSVyUmOFIxIkdeJSNDAIGldCMuUsExwPhoIrjcoACqLuUxvTlnGKpXrpCZhkbsUtUiCnLOtzZhjjFbrXxZSNPwOcCuLTCqzgxnBZrCcBEOevMIaRutODtwpJiRZGqpdQziPNyVwVdLxBwsZpZcVUAgTKjjaHHBFfFXtVrakSIosGVlQILvLiVgLgtFVXaEPwIdpCBuAJRpsRkoFUHKXVoiKFiLGsQaXxxiMCNdFcDVwrlYIiPxwKjbMptVUrPijJHbMYXHHppplksabPCparawfDYUwVIHVlgJZDceJOWfJdSWzUOfvrHUiFrAzrbSQmWrVEPhOpMmErnYBBfvxBPEWMeDkhzqTpbOCYHDfxGPJDiAVAMOcXKvOWIFzGQmZCaeMbRHXLNiANlbXYZprypSTIuJziqwUPctZL"
INFO_KEY = "phVlVbCWHMgWxvBTxGnFwVLjnpelCuhYblZpelJuSRTXrPLQEKfEZDwxfTSBdmpcnVbzukyfEOnaVFNoOPJiSKKdpQqATODUxiiLJgaCmYXNdZsCXVshzZOURPxGvhSBrkxszwsnCbnYqDOiGYOLyRGrDEwPVxASspqFeGYcFDmDGovlqUDGgcQPKHRJMyWaQWbYzzCgOJETIdjEkmvxGnJPwgwnMsxMxQtKyoxLQskYSuSrwNkLCrvZYcqxovRhKFiwxXMRRpwVFNteydZBCwQSGJlWrseMEDKZlfNzlYFEESiAwyMRBghQlaipGkmRvxPcuWWxPSrIolqzzjTLhLIhRUxBbadHJXqoYEFSEsHrWjeGIqHvpgORtlDXYitqWaHJNrffnTryfYqYSvwXgtxTJPZnVbZzMxdtAKsKstOhzokNcsPxqhmSczYHdKTOksjRkBSkZlqHIPOCaWBGjsDAGsoPXqdrurcaOELRHgOcukddAOsRyUepOvwKPZieSwnemmlIKCPeRUtlsTFYJqSTztiQpFmiFHzOLQxwzezRTfvSADoiOzYCSRtANuoyyuKxQHmocYmcEmtbYpisnzJInfJCjFSdCwTIOzWtGQNTFZlPaWQTwVKyQqzoDXTiXEvOZknzdxAmzNARPHPfgVUzQEiCSFTXWiFGmWfowlsPrNUjNrGrRfXTxmsuSuKEUOfvSGmwJqBGDyderfRcGQNzaNSgVrXJOCAnvAWzerznYdxRfTFiGcwdJZqESiujfIAaazlaGxcoExDzsjMkYKJxsXroxVBCNiWFvqqVKFhtqaZJIVDnLxqtufAEWXnzCEPgYAxSJaoITXisyjcmvIqmSfGmVAlqDsBtieTQvbShqgzJylvRxoXpBRPnpRkXlsvmOWZuMauplDcZqAIsyHSymGELLXDYdmYnMPzEYLkkJaHmoyvGFSsPIQkZEnbVEmdaLmeIATnKEeeuvpUJRAhpppBMneuwJKRjtUluLKxdmsiJyobAqoMLIYUejitSIIjrgPAuBYEhhYvtMrQvcPeNXKnCHYIWmSUYWaeQkYRYfbEjSgGMpPDGmgNYOJWkGnGfodApdfAvVVcMqsjEeIWLEylxO"
transaction_headers = {"Content-Type": "application/json; charset=utf-8", "authkey": API_KEY}


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def delete_vendor(requst, acc_no):
    vendor = BankDetails.objects.filter(account_no=acc_no).all()
    if vendor:
        vendor.delete()
        return redirect('webapp:bank-details')
def loadBankList(request):
    resp = requests.post(url=URL, headers=transaction_headers, json={"service": "BNK9901", "request": {}},
                         verify=False)
    resp = resp.json()
    if resp['operation_status'] == 'SUCCESS':
        resp = resp['response']['bankList']

        return JsonResponse(resp, safe=False)


def UserLogin(request):
    if request.method == 'POST':
        try:
            username = request.POST["username"]
            cif = request.POST["cif"]
            password = request.POST["password"]
            print(password)
            user = authenticate(request, username=username, password=password,
                                backend='webapp.myauthBackend.UserAuthBackend')
            if user is not None:
                if user.role == '001':
                    login(request, user)
                    return redirect('webapp:bank-details')
                elif user.role == '002':
                    login(request, user)

                    json = {
                        "service": "CORE_BANKING_LOGIN",
                        "request": {
                            "username": f"{username}",
                            "cif": f"{cif}",
                            "password": f"{password}",
                            "channelType": "CORPORATE"
                        }
                    }

                    resp = requests.post(url=URL, headers=transaction_headers, json=json, verify=False)
                    resp = resp.json()
                    if resp['response']['otpEnable']:
                        cache.set('session_token', f"{resp['response']['session_token']}", timeout=600)
                        json = {
                            "service": "CORE_BANKING_GENERATE_OTP",
                            "request": {
                                "userName": f"{resp['response']['userName']}",
                                "session_token": f"{resp['response']['session_token']}"
                            }
                        }
                        response = requests.post(url=URL, headers=transaction_headers, json=json, verify=False)
                        response = response.json()
                        print(response)
                        if response['response']['otpEnable']:
                            # log_hist = UserLoginHistory(username=username, ipaddress=get_ip_address(request),
                            # timestamp=datetime.datetime.now())
                            # log_hist.save()
                            return redirect('webapp:enter-otp', )
                    else:
                        messages.error(request, message=resp['response']['message'])
                        return redirect("webapp:login")
            else:
                messages.error(request, message="Username/Passowrd not registered")
                return redirect("webapp:login")
        except Exception as e:
            messages.error(request, message="An error occurred. Please try again.")
            print(str(e))
            return redirect("webapp:login")

    else:
        return render(request, 'index.html')


@user_is_approver
def enterOTP(request):
    if request.method == 'POST':
        try:
            otp = request.POST["otp"]
            json = {
                "service": "CORE_BANKING_VERIFY_OTP",
                "request": {
                    "userName": f"{request.user.username}",
                    "otp": f"{otp}",
                    "session_token": f"{cache.get('session_token')}"
                }
            }
            cache.set(request.user.username, otp, timeout=600)  # set the OTP with a timeout of 300 seconds
            resp = requests.post(url=URL, headers=transaction_headers, json=json, verify=False)
            resp = resp.json()
            print(resp)
            if resp['response']['message'] == "Success":
                if request.user.role == '001':
                    return redirect('webapp:bank-details')
                elif request.user.role == '002':
                    return redirect('webapp:homepage')
                else:
                    messages.error(request, message="User Role Unknown")
                    return redirect('webapp:login')
            else:
                messages.error(request, message='Login Failed.Invalid OTP')
                return redirect("webapp:login")
        except Exception as e:
            messages.error(request, message="An error occurred. Please try again.")
            print(str(e))
            return redirect("webapp:login")

    return render(request, 'validate-otp.html')


def checkUserRole(request):
    username = request.GET['username']
    role = Users.objects.filter(username=username).values('role')
    if role:
        return JsonResponse({'role': role[0]})


def UserLogout(request):
    logout(request)
    return redirect('webapp:login')


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        # 👇️ if passed in object is instance of Decimal
        # convert it to a string
        if isinstance(obj, Decimal):
            return str(obj)
        # 👇️ otherwise use the default behavior
        return json.JSONEncoder.default(self, obj)


def get_search_results(request):
    """ Get search results based on query parameters """

    if request.method != 'GET':
        return JsonResponse({'message': 'Only GET requests are allowed'}, status=400)

    try:
        vendor_info = BankDetails.objects.values('vendor_id', 'sort_code',
                                                 'account_no',
                                                 'account_name').all()

        vendors = [vendor['vendor_id'] for vendor in vendor_info]

        # Dictionary containing field mapping parameters
        field_mapping_transactions = {
            'vendor_id': appym.IDVEND.like(f'%{request.GET.get("search_params")}%'),
            'date': appym.DATERMIT.like(f'%{request.GET.get("search_params")}%'),
            'amount': appym.AMTPAYM.like(f'%{request.GET.get("search_params")}%'),
            'invoice_id': appym.IDINVC.like(f'%{request.GET.get("search_params")}%'),
        }

        field_mapping_vendor = {
            'account_number': 'account_no__icontains',
            'sort_code': 'sort_code__icontains',
            'bank_name': 'bank_name__icontains',

        }

        search_params = request.GET.get('search_params')
        field_option = request.GET.get('filter_options')

        if field_option in field_mapping_transactions:
            transaction_info = ms_session.query(appym).filter(appym.IDVEND.in_(vendors),
                                                              field_mapping_transactions[field_option]).all()
            trans_infor_raw = []
            batch_list = [batch.CNTBTCH for batch in transaction_info]
            data = ms_session.query(aptcr).filter(aptcr.CNTBTCH.in_(batch_list))

            for payment, record in zip(transaction_info, data):
                transactions = {
                    'IDINVC': (payment.IDINVC).strip(),
                    'DATERMIT': payment.DATERMIT,
                    'AMTPAYM': payment.AMTPAYM,
                    'IDVEND': (payment.IDVEND).strip(),
                    'REFERENCE': (record.TEXTRMIT).strip()

                }
                trans_infor_raw.append(transactions)
            paginator = Paginator(trans_infor_raw, 20)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'transaction_info': page_obj,
                'vendor_info': vendor_info,
            }

            return render(request, 'homepage.html', context)


        elif field_option in field_mapping_vendor and search_params:
            vendor_info = BankDetails.objects.filter(**{field_mapping_vendor[field_option]: search_params}).values(
                'vendor_id', 'sort_code', 'account_no', 'account_name').all()
            vendor_ids = [vendor['vendor_id'] for vendor in vendor_info]
            trans_infor_raw = []
            transaction_info = ms_session.query(appym).filter(
                appym.IDVEND.in_(vendor_ids)).all()

            batch_list = [batch.CNTBTCH for batch in transaction_info]

            data = ms_session.query(aptcr).filter(aptcr.CNTBTCH.in_(batch_list))

            for payment, record in zip(transaction_info, data):
                transactions = {
                    'IDINVC': (payment.IDINVC).strip(),
                    'DATERMIT': payment.DATERMIT,
                    'AMTPAYM': payment.AMTPAYM,
                    'IDVEND': (payment.IDVEND).strip(),
                    'REFERENCE': (record.TEXTRMIT).strip()

                }
                trans_infor_raw.append(transactions)

            paginator = Paginator(trans_infor_raw, 20)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'transaction_info': page_obj,
                'vendor_info': vendor_info,
                'page_number': page_number
            }

            return render(request, 'homepage.html', context)

    except Exception as e:
        return JsonResponse({'message': f'An error occurred while processing your request {e}'}, status=500)


def format_response_data(page_number, transaction_info, vendor_info):
    """ Format Response data and return a dictionary containing the data"""
    if page_number is None:
        page_data, number_of_pages = paginate_data(transaction_info, 1)
        return {'transaction_info': list(page_data), 'vendor_info': list(vendor_info),
                'number_of_pages': number_of_pages}
    page_data, number_of_pages = paginate_data(transaction_info, int(page_number))

    return {'transaction_info': list(page_data), 'vendor_info': list(vendor_info), 'number_of_pages': number_of_pages}


def serialize_sqlalchemy_object(obj):
    # Get the class mapper for the object
    mapper = class_mapper(obj.__class__)
    # Get the columns from the mapper
    columns = [prop.key for prop in mapper.iterate_properties if hasattr(prop, "columns")]
    # Create a dictionary of the object's attributes
    data = {}
    for colmn in columns:
        data[colmn] = getattr(obj, colmn)
    # Serialize the dictionary as JSON
    return json.dumps(data, cls=DecimalEncoder)


def paginate_data(data, page_number, page_size=10):
    """ Paginate data and return page object and number of pages """
    paginator = CustomPaginator(data, page_size)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj, paginator.num_pages


@login_required(login_url="/")
@user_is_support_staff
def bankUploadViaForm(request):
    try:
        form = BankDetailsForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                if request.htmx:
                    return render(request, 'account-details.html', {'form': form})
                vendor = form.save(commit=False)
                sort_code = form.cleaned_data.get('sort_code')
                resp = requests.post(url=URL, headers=transaction_headers, json={"service": "BNK9901", "request": {}},
                                     verify=False)
                resp = resp.json()
                if resp['operation_status'] == 'SUCCESS':
                    resp = resp['response']['bankList']
                    for resp in resp:
                        if f'{sort_code}' == resp['sortCode']:
                            bicCode = resp['bicCode']
                            vendor.bicCode = bicCode
                            vendor.save()
                            return redirect('webapp:bank-details')
                        else:
                            bicCode = 'ZICB'
                            vendor.bicCode = bicCode
                            vendor.save()
                            return redirect('webapp:bank-details')
                else:
                    return HttpResponse(f'Error saving bank details, Try again later', status=500)

        return render(request, 'account-details.html', {'form': form})
    except Exception as e:
        print(e)


def editBankUploadViaForm(request, acc_id):
    vendor = BankDetails.objects.filter(account_no=acc_id).first()
    form = BankDetailsForm(request.POST, instance=vendor)
    print(vendor)
    if request.method == 'POST':
        if form.is_valid():
            if request.htmx:
                return render(request, 'account-details.html', {'form': form})
            vendor = form.save(commit=False)
            """sort_code = form.clean_sort_code()
            resp = requests.post(url=URL, headers=transaction_headers, json={"service": "BNK9901", "request": {}},
                                 verify=False)
            resp = resp.json()
            if resp['operation_status'] == 'SUCCESS':
                resp = resp['response']['bankList']
                for resp in resp:
                    if f'{sort_code}' == resp['sortCode']:
                        bank_name = resp['bankName']
                        branch = resp['branchDesc']
                        bicCode = resp['bicCode']
                        vendor.bank_name = bank_name
                        vendor.branch = branch
                        vendor.bicCode = bicCode"""
            vendor.save()
            return redirect('webapp:bank-details')
            """else:
                messages.error(request, 'Error saving information, try again later')
                return redirect('webapp:upload-bank-details')"""
        else:
            render(request, 'edit-vendor-bank.html',
                   {'form': BankDetailsForm(instance=vendor), 'acc_id': vendor.account_no})

    return render(request, 'edit-vendor-bank.html', {'form': BankDetailsForm(instance=vendor),
                                                     'acc_id': vendor.account_no})


@login_required(login_url='/')
@user_is_support_staff
def vendorBankDetails(request):
    data = BankDetails.objects.all()
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'bank_details': page_obj,
    }
    return render(request, 'vendor-bank-details.html', context)


@login_required(login_url="/")
@user_is_support_staff
def searchvendorBankDetails(request):
    if request.method == 'GET':
        vendor = request.GET['vendor']
        data = BankDetails.objects.filter(vendor_id=vendor).values('account_no', 'account_name', 'vendor_email',
                                                                   'vendor_id', 'vendor_mobile_number', 'sort_code'
                                                                   , 'branch', 'bank_name')

        return JsonResponse({'vendorinfo': list(data)}, status=200)


@login_required(login_url="/")
@user_is_support_staff
def bankUploadCSV(request):
    errors = []
    upload_errors = {}
    if request.method == 'POST':
        # try:
        file = request.FILES['csvupload']
        df = pd.read_excel(file, dtype={'account_no': str, 'vendor_id': str, 'account_name': str,
                                        'vendor_mobile_number': str, 'vendor_email': str, 'sort_code': str})
        df.fillna("", inplace=True)
        for row in df.itertuples(index=False):
            account_no = row.account_no
            vendor_id = row.vendor_id
            account_name = row.account_name
            vendor_mobile_number = row.vendor_mobile_number
            vendor_email = row.vendor_email
            bank_name = ''
            branch = ''
            sort_code = row.sort_code
            bicCode = ''
            resp = requests.post(url=URL, headers=transaction_headers, json={"service": "BNK9901", "request": {}},
                                 verify=False)
            resp = resp.json()
            if resp['operation_status'] == 'SUCCESS':
                resp = resp['response']['bankList']
                found = False
                for resp_item in resp:
                    if str(sort_code) == resp_item['sortCode']:
                        bank_name = resp_item['bankName']
                        branch = resp_item['branchDesc']
                        bicCode = resp_item['bicCode']
                        found = True
                        break
                if not found:
                    upload_errors = {
                        'errors': [f'Sort Code associated with {account_name} is invalid']
                    }
                    errors.append(upload_errors)
                else:
                    upload_errors = {
                        'errors': []
                    }
                    errors.append(upload_errors)
            isVend = ms_session.query(apven).filter_by(VENDORID=vendor_id).all()
            if not isVend:
                print(upload_errors)
                upload_errors['errors'].append(f'Vendor ID {vendor_id} is invalid')

            if not errors[0]['errors']:
                bank = BankDetails(
                    account_no=account_no,
                    vendor_id=vendor_id,
                    account_name=account_name,
                    vendor_mobile_number=vendor_mobile_number,
                    vendor_email=vendor_email,
                    bank_name=bank_name,
                    sort_code=sort_code,
                    branch=branch,
                    bicCode=bicCode
                )
                bank.save()
                return redirect('webapp:bank-details')
            else:
                messages.error(request, ", ".join(errors[0]['errors']))
                return redirect('webapp:upload-bank-details')

        """ except Exception as e:
            print(e)"""


@login_required(login_url="/")
@user_is_support_staff
def bankUploadCSVTemplate(request):
    try:
        b = io.BytesIO()
        selected_fields = ['account_no', 'vendor_id', 'account_name', 'vendor_mobile_number', 'vendor_email',
                           'sort_code']
        df = pd.DataFrame(columns=selected_fields)
        writer = pd.ExcelWriter(b, engine='openpyxl')
        df.to_excel(writer, sheet_name='vendor bank details', index=False)
        writer.save()

        response = HttpResponse(b.getvalue(),
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Report1.xlsx"'
        return response

    except Exception as e:
        return HttpResponse(f'Error exporting data: {str(e)}', status=500)


def forgotPassword(request):
    return render(request, 'forgot-password.html')

def vendor_account_details(request):
    account_name = request.GET['account_name']
    data = BankDetails.objects.filter(account_name__icontains=account_name).values('account_no', 'sort_code', 'bicCode',
                                                                                   'bank_name')
    return JsonResponse({'account_details': list(data)}, status=200)

def search_invoice_id(request):
    """ Search by idinvc in Request list and return JSON resposne if found """
    if request.method == 'POST':
        if is_ajax(request):
            try:
                # Get invoice ids from request
                invoice_ids = json.loads(request.POST.get('invoice_ids[]'))
                transaction_info = []
                transaction_inf = ms_session.query(appym).filter(appym.IDINVC.in_(invoice_ids)).order_by(
                    appym.CNTBTCH.desc()).all()
                vendor_info = BankDetails.objects.values('vendor_id', 'sort_code', 'account_no', 'account_name').all()
                for t in transaction_inf:
                    t.IDVEND = t.IDVEND.strip()
                    transactions = serialize_sqlalchemy_object(t)
                    transaction_info.append(transactions)
                return JsonResponse(format_response_data(request.GET.get('page_number'),
                                                         transaction_info, vendor_info), safe=False)
            except Exception as e:
                print(e)
                message = 'Error: ' + str(e)
                return JsonResponse({'message': message}, safe=False)
        else:
            return JsonResponse({'message': 'Not an ajax request'}, safe=False)
    else:
        return JsonResponse({'message': 'Not a POST request'}, safe=False)

@login_required(login_url='/')
@user_is_approver
def homepage(request):
    payment_transactions = []
    vendor_info = BankDetails.objects.all()
    processed_dep = ProcessedDeposits.objects.all()
    vendors = [vendor.vendor_id for vendor in vendor_info]
    processed = [processed.invoiceid for processed in processed_dep]
    payment_transactions_raw = ms_session.query(appym).filter(appym.IDVEND.in_(vendors),
                                                              not_(appym.IDINVC.in_(processed))).order_by(
        appym.CNTBTCH.desc()).all()
    batch_list = [batch.CNTBTCH for batch in payment_transactions_raw]
    data = ms_session.query(aptcr).filter(aptcr.CNTBTCH.in_(batch_list)).order_by(aptcr.CNTBTCH.desc()).all()
    for payment, record in zip(payment_transactions_raw, data):
        transactions = {
            'IDINVC': (payment.IDINVC).strip(),
            'DATERMIT': payment.DATERMIT,
            'AMTPAYM': payment.AMTPAYM,
            'IDVEND': (payment.IDVEND).strip(),
            'REFERENCE': (record.TEXTRMIT).strip()

        }
        payment_transactions.append(transactions)

    paginator = Paginator(payment_transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'transaction_info': page_obj,
        'vendor_info': vendor_info,
    }

    return render(request, 'homepage.html', context)


@login_required(login_url="/")
@user_is_approver
def post_transactions(request):
    """ Post transactions to API endpoint """
    successful_keys = []
    unsuccessful_keys = []
    responses = {}
    if request.method == 'POST':
        transacs = json.loads(request.POST.get('transactions'))
        transactions = []
        for entry in transacs:
            values = entry['values']
            transaction_element = {
                'date': values[1],
                'amount': values[2],
                'invoice_id': values[3],
                'remarks': values[4],
                'vendor_id': values[5],
                'account_name': values[6],
                'transaction_type': values[7],
                'account_no': values[8],
                'sort_code': values[9],
                'bicCode': values[10],
                'bank_name': values[11]
            }
            transactions.append(transaction_element)
        for transaction in transactions:
            if transaction['transaction_type'] == 'DDAC':
                response = postDDACTransaction(request, transaction)
                responses[f"{transaction['transaction_type']}-" + f"{transaction['invoice_id']}"] = {
                    "resps": response[0], "stats": response[1]}
            elif transaction['transaction_type'] == 'IFT':
                response = postFTTransaction(request, transaction)
                responses[f"{transaction['transaction_type']}-" + f"{transaction['invoice_id']}"] = {
                    "resps": response[0],
                    "stats": response[1]}
            elif transaction['transaction_type'] == 'RTGS':
                response = postRTGSTransaction(request, transaction)
                responses[f"{transaction['transaction_type']}-" + f"{transaction['invoice_id']}"] = {
                    "resps": response[0],
                    "stats": response[1]}
            elif transaction['transaction_type'] == 'AIRTEL':
                response = postRTGSTransaction(request, transaction)
                responses[f"{transaction['transaction_type']}-" + f"{transaction['invoice_id']}"] = {
                    "resps": response[0],
                    "stats": response[1]}
            elif transaction['transaction_type'] == 'MTN':
                response = postRTGSTransaction(request, transaction)
                responses[f"{transaction['transaction_type']}-" + f"{transaction['invoice_id']}"] = {
                    "resps": response[0],
                    "stats": response[1]}
            elif transaction['transaction_type'] == 'ZAMTEL':
                response = postRTGSTransaction(request, transaction)
                responses[f"{transaction['transaction_type']}-" + f"{transaction['invoice_id']}"] = {
                    "resps": response[0],
                    "stats": response[1]}
            else:
                responses['error'] = {'resps': 'Transaction Type Selected invalid', "stats": 200}
        print(responses)
        for k, v in responses.items():
            if v['resps'] == "Fund Transfer initiated successfully":
                successful_keys.append(k)
            else:
                unsuccessful_keys.append(k)
        if len(unsuccessful_keys) == 0:
            return JsonResponse({"resps": "Fund Transfer initiated successfully", "stats": 200}, safe=False)
        else:
            for key in unsuccessful_keys:
                return JsonResponse({"resps": f"Errors with initiating transactions occured", "stats": 500}, safe=False)
        print(transactions['transaction_type'])

    return JsonResponse({'message': 'GET Request Not Allowed'}, status=400)


@login_required(login_url='/')
@user_is_approver
def transaction_history(request):
    data = ProcessedDeposits.objects.all().order_by('-timestamp')
    paginator = Paginator(data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    all_data = data.filter(timestamp__month__in=range(1, 13))
    grouped_data = groupby(all_data, key=attrgetter('timestamp.month'))
    monthly_data = {month: 0 for month in range(1, 13)}
    for month, data in grouped_data:
        monthly_data[month] = len(list(data))
    monthly_data = [{'month': datetime.date(1900, month, 1).strftime('%B'), 'data': count} for month, count in
                    monthly_data.items()]
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)

    date_range = [end_date - datetime.timedelta(days=x) for x in range(7)]
    processed_deposits = ProcessedDeposits.objects.filter(timestamp__date__range=(start_date, end_date))
    processed_deposits = processed_deposits.annotate(trans_date=TruncDate('timestamp')).values('trans_date').annotate(
        count=Count('trans_date'))
    date_dict = {deposit['trans_date'].strftime('%Y-%m-%d'): deposit['count'] for deposit in processed_deposits}
    date_list = [date.strftime('%Y-%m-%d') for date in date_range]
    count_list = [date_dict.get(date.strftime('%Y-%m-%d'), 0) for date in date_range]
    context = {'transaction_info': page_obj,
               'date_list': date_list,
               'count_list': count_list,
               'data_by_month': monthly_data,
               }

    return render(request, "transaction-history.html", context)


def zicb_customer_account_number_check(request):
    account_no = request.GET['account_no']
    data = {
        "service": "ZB0627",
        "request": {
            "accountNos": f"{account_no}"
        }
    }
    response = requests.post(url=URL, headers={"Content-Type": "application/json; charset=utf-8", "authkey": INFO_KEY},json=data, verify=False)
    response = response.json()
    account_list = response['response']['accountList']
    print(account_list)
    if account_list == []:
        return JsonResponse({'response':False}, safe=False)
    else:
        return JsonResponse({'response': account_list}, safe=False)


def other_bank_account_number_check(request):
    account_no = request.GET['account_no']
    serviceID = request.GET['serviceID']
    data = {
        "service": "MT002",
        "request": {
            "payload": {
                "serviceID": f"{serviceID}",
                "accountNumber": f"{account_no}",
                "currencyCode": "ZMW",
                "countryCode": "260"
            }
        }
    }
    response = requests.post(url=URL,
                             headers={"Content-Type": "application/json; charset=utf-8", "authkey": INFO_KEY},
                             json=data, verify=False)
    response = response.json()
    if response["response"]["results"]["statusDescription"] == "Account number provided is valid":
        return response['response']['results']
    else:
        return False
def checkAccNumber(request):
    acc = request.GET.get('acc_name')
    account_number = BankDetails.objects.filter(account_name__icontains=acc).values('account_no')
    acc_no = [acc_no for acc_no in account_number]
    print(acc_no)
    data = {
        "service": "ZB0627",
        "request": {
            "accountNos": f"{acc_no}"
        }
    }
    response = requests.post(url=URL, headers={"Content-Type": "application/json; charset=utf-8", "authkey": INFO_KEY},
                             json=data, verify=False)
    response = response.json()
    account_list = response['response']['accountList']
    return JsonResponse({'resp': list(account_list)})


def postDDACTransaction(request, transaction):
    token = cache.get('session_token')
    otp = cache.get(request.user.username)
    data = {
        "service": "CORE_BANKING_FT",
        "request": {
            "username": f"{request.user.username}",
            "session_token": f"{token}",
            "ftList": [
                {
                    "amount": f"{transaction['amount']}",
                    "remarks": f"{transaction['remarks']}",
                    "bankCode": "01",
                    "bankName": f"{transaction['bank_name']}",
                    "benName": f"{transaction['account_name']}",
                    "beneEmail": "",
                    "benePhoneno": "",
                    "branchCode": "001",
                    "destinationAccount": f"{transaction['account_no']}",
                    "destinationCurrency": "ZMW",
                    "nationalClearingCode": "00000",
                    "sourceAccount": "1010036875921",
                    "sourceBranch": "001",
                    "srcCurrency": "ZMW",
                    "swiftCode": f"{transaction['sort_code']}",
                    "transferTyp": "DDACC",
                    "beneTransfer": False,
                    "sortCode": f"{transaction['sort_code']}",
                    "bicCode": f"{transaction['bicCode']}"
                }
            ]
        }
    }

    response = requests.post(url=URL,
                             headers={"Content-Type": "application/json; charset=utf-8", "authkey": API_KEY},
                             json=data, verify=False)

    resp_json = response.json()
    if "randomKey" not in resp_json["response"]:
        return resp_json['response']['message'], 500
    else:
        key = resp_json["response"]["randomKey"]
        req = resp_json["request"]["ftList"]
        ddac_confirm = {
            "service": "CORE_BANKING_FT_CONFIRM",
            "request": {
                "username": "MumbaM",
                "session_token": f"{token}",
                "bulkTransfer": False,
                "randomKey": f"{key}",
                "otp": f"{otp}",
                "ftList": req
            }
        }
        resp = requests.post(url=URL,
                             headers={"Content-Type": "application/json; charset=utf-8", "authkey": IFT_KEY},
                             json=ddac_confirm, verify=False)
        ft_resp_json = resp.json()
        print(ft_resp_json)
        if ft_resp_json['response']['message'] == "Fund Transfer initiated successfully":
            processed = ProcessedDeposits(amount=transaction['amount'], transaction_date=transaction['date'],
                                          vendorid=transaction['account_name'],
                                          invoiceid=transaction['invoice_id'],
                                          vendorname=transaction['account_name'], status=1,
                                          transaction_type="DDAC",
                                          processed_by=request.user.username)
            processed.save()
            return ft_resp_json['response']['message'], 200
        else:
            return ft_resp_json['response']['message'], 500


def postRTGSTransaction(request, transaction):
    token = cache.get('session_token')
    otp = cache.get(request.user.username)

    data = {
        "service": "CORE_BANKING_FT",
        "request": {
            "username": request.user.username,
            "session_token": token,
            "ftList": [
                {
                    "amount": transaction['amount'],
                    "remarks": transaction['remarks'],
                    "bankCode": "01",
                    "bankName": transaction['bank_name'],
                    "benName": transaction['account_name'],
                    "beneEmail": "",
                    "benePhoneno": "",
                    "branchCode": "001",
                    "destinationAccount": transaction['account_no'],
                    "destinationCurrency": "ZMW",
                    "nationalClearingCode": "00000",
                    "sourceAccount": "1010036875921",
                    "sourceBranch": "001",
                    "srcCurrency": "ZMW",
                    "swiftCode": transaction['sort_code'],
                    "transferTyp": "RTGS",
                    "beneTransfer": False,
                    "sortCode": transaction['sort_code'],
                    "bicCode": transaction['bicCode']
                }
            ]
        }
    }

    response = requests.post(url=URL,
                             headers={"Content-Type": "application/json; charset=utf-8", "authkey": API_KEY},
                             json=data, verify=False)

    resp_json = response.json()
    if "randomKey" not in resp_json["response"]:
        return resp_json['response']['message'], 500
    else:
        key = resp_json["response"]["randomKey"]
        req = resp_json["request"]["ftList"]
        rtgs_confirm = {
            "service": "CORE_BANKING_FT_CONFIRM",
            "request": {
                "username": "MumbaM",
                "session_token": token,
                "bulkTransfer": False,
                "randomKey": key,
                "otp": otp,
                "ftList": req
            }
        }
        resp = requests.post(url=URL,
                             headers={"Content-Type": "application/json; charset=utf-8", "authkey": IFT_KEY},
                             json=rtgs_confirm, verify=False)
        ft_resp_json = resp.json()
        if ft_resp_json['response']['message'] == "Fund Transfer initiated successfully":

            processed = ProcessedDeposits(amount=transaction['amount'], transaction_date=transaction['date'],
                                          vendorid=transaction['account_name'],
                                          invoiceid=transaction['invoice_id'],
                                          vendorname=transaction['account_name'], status=1,
                                          transaction_type="RTGS", processed_by=request.user.username)
            processed.save()

            return ft_resp_json['response']['message'], 200
        else:
            return ft_resp_json['response']['message'], 500


def postFTTransaction(request, transaction):
    token = cache.get('session_token')
    json = {
        "service": "CORE_BANKING_FT",
        "request": {
            "username"f"{request.user.username}"
            "session_token": f"{token}",
            "ftList": [
                {
                    "amount": f"{transaction['amount']}",
                    "remarks": f"{transaction['remarks']}",
                    "bankCode": "0000",
                    "bankName": "",
                    "benName": "",
                    "beneEmail": "",
                    "benePhoneno": "",
                    "branchCode": "001",
                    "destinationAccount": f"{transaction['account_no']}",
                    "destinationBranch": "",
                    "destinationCurrency": "",
                    "nationalClearingCode": "00000",
                    "sourceAccount": "1010036875921",
                    "sourceBranch": "001",
                    "srcCurrency": "ZMW",
                    "swiftCode": "0000",
                    "transferTyp": "IAT",
                    "beneTransfer": False
                }
            ]
        }
    }
    print(json)
    response = requests.post(url=URL,
                             headers={"Content-Type": "application/json; charset=utf-8", "authkey": IFT_KEY},
                             json=json, verify=False)
    resp_json = response.json()
    response = resp_json['response']
    if 'randomKey' not in response:
        return response['message'], 500
    else:
        key = resp_json["response"]["randomKey"]
        req = resp_json["request"]["ftList"]
        otp = cache.get(request.user.username)
        ft_confirm_json = {
            "service": "CORE_BANKING_FT_CONFIRM",
            "request": {
                "username": f"{request.user.username}",
                "session_token": f"{token}",
                "bulkTransfer": False,
                "randomKey": f"{key}",
                "otp": f"{otp}",
                "ftList": req
            }
        }
    resp = requests.post(url=URL, headers={"Content-Type": "application/json; charset=utf-8", "authkey": IFT_KEY},
                         json=ft_confirm_json, verify=False)
    ft_resp_json = resp.json()
    if ft_resp_json['response']['message'] == "Fund Transfer initiated successfully":
        processed = ProcessedDeposits(amount=transaction['amount'], transaction_date=transaction['date'],
                                      vendorid=transaction['account_name'],
                                      invoiceid=transaction['invoice_id'],
                                      vendorname=transaction['account_name'], status=1,
                                      transaction_type="IFT", processed_by=request.user.username)

        processed.save()
        return ft_resp_json['response']['message'], 200
    else:
        return ft_resp_json['response']['message'], 500


def postZamtelTransfer(request, transaction):
    data = {
        "service": "CORE_BANKING_MOBILE_MONEY_VERIFY",
        "request": {
            "userName": f"{request.user.username}",
            "customerId": "0036875",
            "requestId": "STMBVERIFY",
            "sourceAccount": "1010036875921",
            "amount": f"{transaction['amount']}",
            "srcCurrency": "ZMW",
            "sourceBranch": "001",
            "parentAccountType": "Mobile Money",
            "serviceId": "4759",
            "transferTyp": "CASHOUT",
            "accountTyp": "ZAMTEL",
            "receiverMobileNo": "260950003968",
            "receiverEmail": "",
            "remarks": f"{transaction['remarks']}"
        }
    }
    response = requests.post(url=URL,
                             headers={"Content-Type": "application/json; charset=utf-8", "authkey": IFT_KEY},
                             json=data, verify=False)
    resp_json = response.json()
    response = resp_json['response']
    if "randomKey" not in response:
        return resp_json['response']['message'], 500
    else:
        token = cache.get('session_token')
        zamtel_confirm_json = {
            {
                "service": "CORE_BANKING_MOBILE_MONEY_VERIFY",
                "request": {
                    "userName": "MumbaM",
                    "session_token": f"{token}",
                    "sourceAccount": "1010036875921",
                    "amount": f"{transaction['amount']}",
                    "srcCurrency": "ZMW",
                    "sourceBranch": "001",
                    "parentAccountType": "Mobile Money",
                    "serviceId": "4759",
                    "transferTyp": "CASHOUT",
                    "accountTyp": "ZAMTEL",
                    "receiverMobileNo": "260950003968",
                    "receiverEmail": "",
                    "remarks": f"{transaction['remarks']}"
                }
            }
        }
    resp = requests.post(url=URL, headers={"Content-Type": "application/json; charset=utf-8", "authkey": IFT_KEY},
                         json=zamtel_confirm_json, verify=False)
    ft_resp_json = resp.json()
    print(ft_resp_json)
    if ft_resp_json['response']['message'] == "Fund Transfer initiated successfully":
        processed = ProcessedDeposits(amount=transaction['amount'], transaction_date=transaction['date'],
                                      vendorid=transaction['account_name'],
                                      invoiceid=transaction['invoice_id'],
                                      vendorname=transaction['account_name'], status=1,
                                      transaction_type="ZAMTEL CASHOUT", processed_by=request.user.username)

        processed.save()
        return ft_resp_json['response']['message'], 200
    else:
        return ft_resp_json['response']['message'], 500


def postMTNTransfer(request, transaction):
    data = {
        "service": "CORE_BANKING_MOBILE_MONEY_VERIFY",
        "request": {
            "userName": f"{request.user.username}",
            "customerId": "0036875",
            "requestId": "STMBVERIFY",
            "sourceAccount": "1010036875921",
            "amount": f"{transaction['amount']}",
            "srcCurrency": "ZMW",
            "sourceBranch": "001",
            "parentAccountType": "Mobile Money",
            "serviceId": "4756",
            "transferTyp": "CASHOUT",
            "accountTyp": "MTN",
            "receiverMobileNo": "260966855355",
            "receiverEmail": "",
            "remarks": f"{transaction['remarks']}"
        }
    }
    response = requests.post(url=URL,
                             headers={"Content-Type": "application/json; charset=utf-8", "authkey": IFT_KEY},
                             json=data, verify=False)
    resp_json = response.json()
    response = resp_json['response']
    if "randomKey" not in response:
        return resp_json['response']['message'], 500
    else:
        token = cache.get('session_token')
        mtn_confirm_json = {
            {
                "service": "CORE_BANKING_MOBILE_MONEY_VERIFY",
                "request": {
                    "userName": f"{request.user.username}",
                    "session_token": f"{token}",
                    "sourceAccount": "1010036875921",
                    "amount": f"{transaction['amount']}",
                    "srcCurrency": "ZMW",
                    "sourceBranch": "001",
                    "parentAccountType": "Mobile Money",
                    "serviceId": "4756",
                    "transferTyp": "CASHOUT",
                    "accountTyp": "MTN",
                    "receiverMobileNo": "260966855355",
                    "receiverEmail": "",
                    "remarks": f"{transaction['remarks']}"
                }
            }
        }
    resp = requests.post(url=URL, headers={"Content-Type": "application/json; charset=utf-8", "authkey": IFT_KEY},
                         json=mtn_confirm_json, verify=False)
    ft_resp_json = resp.json()
    print(ft_resp_json)
    if ft_resp_json['response']['message'] == "Fund Transfer initiated successfully":
        processed = ProcessedDeposits(amount=transaction['amtpaym'], transaction_date=transaction['date'],
                                      vendorid=transaction['account_name'],
                                      invoiceid=transaction['invoice_id'],
                                      vendorname=transaction['account_name'], status=1,
                                      transaction_type="MTN CASHOUT", processed_by=request.user.username)

        processed.save()
        return ft_resp_json['response']['message'], 200
    else:
        return ft_resp_json['response']['message'], 500


def postAirtelTransfer(request, transaction):
    data = {
        "service": "CORE_BANKING_MOBILE_MONEY_VERIFY",
        "request": {
            "userName": f"{request.user.username}",
            "customerId": "0036875",
            "requestId": "STMBVERIFY",
            "sourceAccount": "1010036875921",
            "amount": f"{transaction['amount']}",
            "srcCurrency": "ZMW",
            "sourceBranch": "001",
            "parentAccountType": "Mobile Money",
            "serviceId": "4755",
            "transferTyp": "CASHOUT",
            "accountTyp": "AIRTEL",
            "receiverMobileNo": "0978980412",
            "receiverEmail": "",
            "remarks": f"{transaction['remarks']}"
        }
    }
    response = requests.post(url=URL,
                             headers={"Content-Type": "application/json; charset=utf-8", "authkey": IFT_KEY},
                             json=data, verify=False)
    resp_json = response.json()
    response = resp_json['response']
    if "randomKey" not in response:
        return resp_json['response']['message'], 500
    else:
        token = cache.get('session_token')
        airtel_confirm_json = {
            {
                "service": "CORE_BANKING_MOBILE_MONEY_VERIFY",
                "request": {
                    "userName": f"{request.user.username}",
                    "session_token": f"{token}",
                    "sourceAccount": "1010036875921",
                    "amount": f"{transaction['amount']}",
                    "srcCurrency": "ZMW",
                    "sourceBranch": "001",
                    "parentAccountType": "Mobile Money",
                    "serviceId": "4755",
                    "transferTyp": "CASHOUT",
                    "accountTyp": "AIRTEL",
                    "receiverMobileNo": "0978980412",
                    "receiverEmail": "",
                    "remarks": f"{transaction['remarks']}"
                }
            }
        }
    resp = requests.post(url=URL, headers={"Content-Type": "application/json; charset=utf-8", "authkey": IFT_KEY},
                         json=airtel_confirm_json, verify=False)
    ft_resp_json = resp.json()
    print(ft_resp_json)
    if ft_resp_json['response']['message'] == "Fund Transfer initiated successfully":
        processed = ProcessedDeposits(amount=transaction['amount'], transaction_date=transaction['date'],
                                      vendorid=transaction['account_name'],
                                      invoiceid=transaction['invoice_id'],
                                      vendorname=transaction['account_name'], status=1,
                                      transaction_type="Airtel CASHOUT", processed_by=request.user.username)

        processed.save()
        return ft_resp_json['response']['message'], 200
    else:
        return ft_resp_json['response']['message'], 500
