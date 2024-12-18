import os
import uuid
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta

FDI_SECRET_KEY = os.getenv('NOTIFICATION_FDI_SECRET_KEY')
FDI_ACCOUNT_ID = os.getenv('NOTIFICATION_FDI_ACCOUNT_ID')
FDI_SENDER_ID = os.getenv('NOTIFICATION_FDI_SENDER_ID')
FDI_BASE_URL = os.getenv('NOTIFICATION_FDI_BASE_URL')



class FDISmsClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.base_url = FDI_BASE_URL
        self.sender_id = FDI_SENDER_ID
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
            "api_username": self.account_id,
            "api_password": self.secret_key
        }
        
        response = requests.post(
            endpoint,
            json=payload,
            headers=self._get_headers(with_auth=False)
        )
        response.raise_for_status()
        
        data = response.json()
        self.token = data['access_token']
        # Parse expiry time from response and set it 5 minutes earlier for safety
        expiry = datetime.strptime(data['expires_at'], '%Y-%m-%dT%H:%M:%SZ')
        self.token_expiry = expiry - timedelta(minutes=5)
        
    def send_single_notification(self, message: str, recipient: str) -> None:
        """Send a notification to a recipient"""
        
        """Initiate a payment transaction"""
        self._refresh_token_if_needed()
        
        
        endpoint = f"{self.base_url}/mt/single"
        payload = {
            "msisdn": recipient,
            "message": message,
            "msgRef": str(uuid.uuid4()),
            "dlr": None,
            "sender_id": self.sender_id
        }
        
        response = requests.post(
            endpoint,
            json=payload,
            headers=self._get_headers()
        )
        response.raise_for_status()
        
        return response.json()
    
    
    def send_bulk_notification(self, message: str, recipients: List[str]) -> None:
        """Send a notification to multiple recipients"""
        
        """Initiate a payment transaction"""
        self._refresh_token_if_needed()
        
        
        endpoint = f"{self.base_url}/mt/bulk"
        payload = {
            "msisdn_list": recipients,
            "message": message,
            "msgRef": str(uuid.uuid4()),
            "dlr": None,
            "sender_id": self.sender_id
        }
        
        response = requests.post(
            endpoint,
            json=payload,
            headers=self._get_headers()
        )
        
        response.raise_for_status()
        
        return response.json()