import json

import requests
from django.forms import forms, ModelForm

from .models import BankDetails
from .services import ms_session, apven

URL = "https://41.175.13.198:7664/api/json/commercials/zicb/banking"
API_KEY = "jVKRmqnoqsmoMXfhgaEjeXKctmtWdMpaPKINOfaiglVaWkVraFYngtYcfspiitZIcKjfZUwPTPHRNUrIgdiAyqpgplQFDJYwDCvzdUnnxalobZxzOCMWVKhVQZYiEfukQUCTeXOhKAIXTWSLszsFmuwZAGwTmpBUTjraYerObIOEAJbmEffhhxRgsglFAPPkKVCIzNkyzCaMxyIuNVdjHURqzqimwoPfkugKrgBNCTOZWYrUVyXKbGaeUayugjUFfbdboEOwipAQxQgTDrfpBGcSVELjqtrqTtlElIShCwUErSqvZVGneqWXEvuRwOqbVtJSbqZyReGCpRyXaivqoDSycUpDYnSymrcwQBDSTZRVIKALobWZxHQpVeTCfEhqDqfMydQqVjRpSaljyIRoIXDkhqhuEsZWVKZmgcbPxvTPSAuCoIvYfjdoFRZVemldnYZctyjTUTtmfiQQPRibOHwVEbstjZacCLHwgXPxtzRtdSypEjJcdkCUnfulNPtlSheLzNgtpAdQjWcuruYNtIgreCZELvbYxxYDlwWIngVmuzLTERviDjwYjeaeVnJxWecdIeLylpLKNHPobrXnJBltzgknhsqdKlKtoRqQobuvoCGVySOoTDPFhzjjeZGscCOvgKecixZdgXrRnghhsCuefYzgiCrHzmAaObiHIKPWxuFJkBaXxhNYOjSVyUmOFIxIkdeJSNDAIGldCMuUsExwPhoIrjcoACqLuUxvTlnGKpXrpCZhkbsUtUiCnLOtzZhjjFbrXxZSNPwOcCuLTCqzgxnBZrCcBEOevMIaRutODtwpJiRZGqpdQziPNyVwVdLxBwsZpZcVUAgTKjjaHHBFfFXtVrakSIosGVlQILvLiVgLgtFVXaEPwIdpCBuAJRpsRkoFUHKXVoiKFiLGsQaXxxiMCNdFcDVwrlYIiPxwKjbMptVUrPijJHbMYXHHppplksabPCparawfDYUwVIHVlgJZDceJOWfJdSWzUOfvrHUiFrAzrbSQmWrVEPhOpMmErnYBBfvxBPEWMeDkhzqTpbOCYHDfxGPJDiAVAMOcXKvOWIFzGQmZCaeMbRHXLNiANlbXYZprypSTIuJziqwUPctZL"
transaction_headers = {"Content-Type": "application/json; charset=utf-8", "authkey": API_KEY}


class BankDetailsForm(ModelForm):
    def __int__(self, *args, **kwargs):
        super(BankDetailsForm, *args, **kwargs)
        self.fields['account_no'].label = "Account Number"
        self.fields['vendor_id'].label = "Vendor ID"
        self.fields['account_name'].label = "Account Name"
        self.fields['vendor_mobile_number'].label = "Vendor Mobile Number"
        self.fields['vendor_email'].label = "Vendor Email"
        self.fields['sort_code'].label = "Sort Code"



    def clean_vendor_id(self):
        try:
            vendor_id = self.cleaned_data.get('vendor_id')
            isVend = ms_session.query(apven).filter_by(VENDORID=vendor_id).all()
            if isVend:
                return vendor_id
            else:
                raise forms.ValidationError('No Vendor With That Vendor ID')
        except Exception as e:
            print(e)

    class Meta:
        model = BankDetails
        fields = ['account_no', 'account_name', 'vendor_id', 'vendor_email', 'vendor_mobile_number', 'bank_name',
                  'branch', 'sort_code']
        error_messages = {
            'account_no': {
                'required': 'Please enter the Account Number.',
                'null': 'The Account Number entered is invalid.',
            },
            'vendor_id': {
                'required': 'Please enter the Vendor ID.',
                'null': 'No Vendor available with Vendor ID entered.',
            },
            'account_name': {
                'required': 'Please enter the account name.',
                'null': 'The Account Name cannot be null.',
            },
            'vendor_mobile_number': {
                'required': 'Please enter the Vendor Mobile Number.',
                'null': 'The Vendor Mobile Number cannot be null.',
            },
            'vendor_email': {
                'required': 'Please enter the Vendor Email.',
                'null': 'The Vendor Email cannot be null.',
            },
            'sort_code': {
                'required': 'Please enter the Sort Code.',
                'null': 'The Sort Code entered is invalid .',
            },
        }
