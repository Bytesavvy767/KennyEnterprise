import requests
import base64
from datetime import datetime
from config import Config


def get_access_token():
    """Retrieve access token from Safaricom OAuth API."""
    key = Config.MPESA_CONSUMER_KEY
    secret = Config.MPESA_CONSUMER_SECRET
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    r = requests.get(url, auth=(key, secret))
    r.raise_for_status()
    return r.json().get('access_token')


def stk_push(phone, amount, account_ref='Order', description='Payment'):
    """Send STK Push request."""
    token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password_str = Config.MPESA_SHORTCODE + Config.MPESA_PASSKEY + timestamp
    password = base64.b64encode(password_str.encode()).decode('utf-8')

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "BusinessShortCode": Config.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": Config.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": Config.MPESA_CALLBACK_URL,
        "AccountReference": account_ref,
        "TransactionDesc": description
    }
    url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()
