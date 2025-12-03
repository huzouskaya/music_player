import requests
import json
import os
from typing import Optional, Dict
from .device_fingerprint import DeviceFingerprint

class AccountManager:
    def __init__(self, server_url: str = "http://localhost:5000"):
        self.server_url = server_url
        self.token = None
        self.user_id = None
        self.device_hash = DeviceFingerprint.get_fingerprint()
        self.load_token()
        
    def register(self, email: str, password: str) -> bool:
        try:
            response = requests.post(
                f"{self.server_url}/api/register",
                json={'email': email, 'password': password},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.token = data['token']
                    self.user_id = data['user_id']
                    self.save_token()
                    return True
            return False
        except Exception:
            return False
    
    def login(self, email: str, password: str) -> bool:
        try:
            response = requests.post(
                f"{self.server_url}/api/login",
                json={'email': email, 'password': password},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.token = data['token']
                    self.user_id = data['user_id']
                    self.save_token()
                    return True
            return False
        except Exception:
            return False
    
    def check_subscription(self) -> Optional[Dict]:
        if not self.token:
            return None

        try:
            headers = {'Authorization': self.token}
            response = requests.post(
                f"{self.server_url}/api/check_subscription",
                json={'device_hash': self.device_hash},
                headers=headers,
                timeout=10
            )

            return response.json() if response.status_code == 200 else None
        except Exception:
            return None
    
    def create_payment(self, plan_type: str) -> Optional[Dict]:
        if not self.token:
            return None

        try:
            headers = {'Authorization': self.token}
            amount = 100.0 if plan_type == 'monthly' else 1000.0

            response = requests.post(
                f"{self.server_url}/api/create_payment",
                json={'plan_type': plan_type, 'amount': amount},
                headers=headers,
                timeout=10
            )

            return response.json() if response.status_code == 200 else None
        except Exception:
            return None
    
    def get_account_info(self) -> Optional[Dict]:
        if not self.token:
            return None

        try:
            headers = {'Authorization': self.token}
            response = requests.get(
                f"{self.server_url}/api/account_info",
                headers=headers,
                timeout=10
            )

            return response.json() if response.status_code == 200 else None
        except Exception:
            return None
    
    def remove_device(self, device_hash: str) -> bool:
        if not self.token:
            return False

        try:
            headers = {'Authorization': self.token}
            response = requests.post(
                f"{self.server_url}/api/remove_device",
                json={'device_hash': device_hash},
                headers=headers,
                timeout=10
            )

            return response.status_code == 200 and response.json().get('success', False)
        except Exception:
            return False

    def activate_license(self, activation_key: str) -> Optional[Dict]:
        try:
            response = requests.post(
                f"{self.server_url}/api/activate_license",
                json={'activation_key': activation_key, 'device_hash': self.device_hash},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data
            return None
        except Exception:
            return None

    def save_token(self):
        """Save token to file for auto-login"""
        if self.token:
            try:
                with open('user_token.json', 'w') as f:
                    json.dump({'token': self.token, 'user_id': self.user_id}, f)
            except Exception:
                pass

    def load_token(self):
        """Load token from file for auto-login"""
        if os.path.exists('user_token.json'):
            try:
                with open('user_token.json', 'r') as f:
                    data = json.load(f)
                    self.token = data.get('token')
                    self.user_id = data.get('user_id')
            except Exception:
                pass
