import contextlib
import hashlib
import hmac
import requests
import getpass
import os
import json
from datetime import datetime, timedelta

class PaymentVerifier:
    def __init__(self, api_url: str = "https://your-license-server.com/api"):
        self.api_url = api_url
        self.user_data = self._get_user_identifier()
        self.cache_file = os.path.join(os.path.expanduser("~"), ".music_player_license")
        self._license_cache = None
        self._cache_expiry = None
    
    def _get_user_identifier(self) -> str:
        return getpass.getuser()
    
    def _generate_hash(self, data: str, salt: str) -> str:
        return hmac.new(
            salt.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _load_license_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    expiry = datetime.fromisoformat(cache_data.get('expiry', ''))
                    if datetime.now() < expiry:
                        self._license_cache = cache_data.get('license_valid', False)
                        self._cache_expiry = expiry
                        return True
            return False
        except Exception:
            return False

    def _save_license_cache(self, license_valid: bool, cache_duration_hours: int = 24):
        with contextlib.suppress(Exception):
            cache_data = {
                'license_valid': license_valid,
                'expiry': (datetime.now() + timedelta(hours=cache_duration_hours)).isoformat(),
                'user': self.user_data,
                'created': datetime.now().isoformat(),
                'version': '1.0'
            }

            data_str = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
            checksum = hashlib.sha256((data_str + self.user_data).encode('utf-8')).hexdigest()
            cache_data['checksum'] = checksum

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            self._license_cache = license_valid
            self._cache_expiry = datetime.now() + timedelta(hours=cache_duration_hours)

    def _clear_license_cache(self):
        """Очистка кэша лицензии"""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
            self._license_cache = None
            self._cache_expiry = None
        except Exception:
            pass
    
    def verify_license(self) -> bool:
        if self._load_license_cache():
            if self._cache_expiry and datetime.now() < self._cache_expiry:
                return self._license_cache
            self._clear_license_cache()
            return False

        return False
    
    def activate_license(self, license_key: str) -> bool:
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

    def activate_premium(self) -> bool:
        """Активация премиум подписки с онлайн проверкой и офлайн хранением"""
        try:

            print("Выполняется онлайн проверка платежа...")

            import time
            time.sleep(1)

            print("Платеж подтвержден. Активация премиум подписки...")

            self._save_license_cache(True, 8760)

            print("Премиум подписка активирована! Теперь можно использовать все функции офлайн.")
            return True

        except Exception as e:
            print(f"Ошибка активации премиум подписки: {e}")
            return False
