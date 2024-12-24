import os
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta

FDI_SECRET_KEY = os.getenv('PAYMENT_FDI_SECRET_KEY')
FDI_ACCOUNT_ID = os.getenv('PAYMENT_FDI_ACCOUNT_ID')
FDI_APP_ID = os.getenv('PAYMENT_FDI_APP_ID')
FDI_BASE_URL = os.getenv('PAYMENT_FDI_BASE_URL')
FDI_CALLBACK_URL = os.getenv('PAYMENT_FDI_CALLBACK_URL')
FDI_CODENAME = 'FDI'


class FDIClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.base_url = FDI_BASE_URL
        self.app_id = FDI_APP_ID
        self.secret_key = FDI_SECRET_KEY
        self.account_id = FDI_ACCOUNT_ID
        self.token = None
        self.token_expiry = None

    def _get_headers(self, with_auth: bool = True) -> Dict:
        """Get request headers, optionally including auth token"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if with_auth and self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def _refresh_token_if_needed(self):
        """Check and refresh token if expired or missing"""
        if not self.token or not self.token_expiry or datetime.now() >= self.token_expiry:
            self.authenticate()

    def authenticate(self) -> None:
        """Authenticate with FDI API and get access token"""
        endpoint = f"{self.base_url}/auth"
        payload = {
            "appId": self.app_id,
            "secret": self.secret_key
        }
        
        response = requests.post(
            endpoint,
            json=payload,
            headers=self._get_headers(with_auth=False)
        )
        response.raise_for_status()
        
        data = response.json()
        self.token = data['data']['token']
        # Parse expiry time from response and set it 5 minutes earlier for safety
        expiry = datetime.fromisoformat(data['data']['expires_at'])
        self.token_expiry = expiry - timedelta(minutes=5)

    def initiate_payment(self, amount: float, reference: str, customer_data: Dict) -> Dict:
        """Initiate a payment transaction"""
        self._refresh_token_if_needed()
        
        endpoint = f"{self.base_url}/momo/pull"
        # Determine channel ID based on phone number prefix
        msisdn = customer_data.get('msisdn')
        if msisdn.startswith(('078', '079')):
            channel_id = 'momo-mtn-rw'
        elif msisdn.startswith(('072', '073')):
            channel_id = 'momo-airtel-rw'
        else:
            raise ValueError("Invalid phone number prefix. Must start with 078/079 for MTN or 072/073 for Airtel")

        payload = {
            "trxRef": reference,
            "channelId": channel_id,
            "accountId": self.account_id,
            "msisdn": msisdn,
            "amount": amount,
            "callback": FDI_CALLBACK_URL
        }
        
        response = requests.post(
            endpoint,
            json=payload,
            headers=self._get_headers()
        )
        response.raise_for_status()
        response_data = response.json()
        return (payload, {
            'transaction_id': response_data['data']['gwRef'],
            'reference': response_data['data']['trxRef'],
            'status': response_data['data']['state'],
            'message': response_data['data'].get('message', '')
        })
        

    def check_payment_status(self, transaction_id: str) -> Dict:
        """Check the status of a payment transaction"""
        self._refresh_token_if_needed()
        
        endpoint = f"{self.base_url}/momo/trx/{transaction_id}/info"
        response = requests.get(
            endpoint,
            headers=self._get_headers()
        )
        response.raise_for_status()
        response_data = response.json()
        return {
            'transaction_id': transaction_id,
            'reference': response_data['data']['trxRef'], 
            'status': response_data['data']['trxStatus'],
            'channel_status': response_data['data']['channelTrxStatus'],
            'channel_message': response_data['data']['channelMsg'],
            'amount': response_data['data']['amount'],
            'currency': response_data['data']['currency'],
            'created_at': response_data['data']['createdAt']
        }

    def process_callback(self, callback_data: Dict) -> Dict:
        """Process callback data from FDI"""
        data = callback_data.get('data', {})
        
        result = {
            'transaction_id': data.get('gwRef'),
            'reference': data.get('trxRef'),
            'status': data.get('state')
        }

        if callback_data.get('status') == 'fail':
            result['error_message'] = data.get('message')

        if data.get('channelRef'):
            result['channel_reference'] = data.get('channelRef')

        return result


