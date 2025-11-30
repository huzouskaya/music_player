import hashlib
import hmac
import requests
import getpass

class PaymentVerifier:
    def __init__(self, api_url: str = "https://your-license-server.com/api"):
        self.api_url = api_url
        self.user_data = self._get_user_identifier()
    
    def _get_user_identifier(self) -> str:
        """Получение идентификатора пользователя"""
        return getpass.getuser()
    
    def _generate_hash(self, data: str, salt: str) -> str:
        """Генерация хэша с солью"""
        return hmac.new(
            salt.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def verify_license(self) -> bool:
        """Проверка лицензии"""
        try:
            response = requests.get(f"{self.api_url}/get_salt")
            if response.status_code != 200:
                return False
            
            salt_data = response.json()
            salt = salt_data.get('salt')
            
            if not salt:
                return False
            
            hashed_user = self._generate_hash(self.user_data, salt)
            
            license_check = {
                'user_hash': hashed_user,
                'salt': salt
            }
            
            response = requests.post(
                f"{self.api_url}/verify_license",
                json=license_check,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('valid', False)
            
            return False
            
        except Exception as e:
            print(f"Ошибка проверки лицензии: {e}")
            return False
    
    def activate_license(self, license_key: str) -> bool:
        """Активация лицензии"""
        try:
            activation_data = {
                'license_key': license_key,
                'user_identifier': self.user_data
            }
            
            response = requests.post(
                f"{self.api_url}/activate_license",
                json=activation_data,
                headers={'Content-Type': 'application/json'}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Ошибка активации лицензии: {e}")
            return False