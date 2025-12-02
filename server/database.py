import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List

class Database:
    def __init__(self, db_path='licenses.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_type TEXT NOT NULL,  -- 'monthly' или 'yearly'
                price REAL NOT NULL,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                auto_renew BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                device_hash TEXT NOT NULL,
                device_name TEXT,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                UNIQUE(user_id, device_hash),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subscription_id INTEGER,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'RUB',
                status TEXT DEFAULT 'pending',  -- pending, completed, failed, refunded, activated
                payment_date TIMESTAMP,
                activated_at TIMESTAMP,  -- Время активации
                transaction_id TEXT UNIQUE,
                payment_method TEXT,
                activation_key TEXT UNIQUE,  -- Старый ключ активации для email
                server_key TEXT,  -- Серверный ключ активации
                client_key TEXT UNIQUE,  -- Клиентский ключ активации
                key_expires TIMESTAMP,  -- Срок действия ключа
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_user(self, email: str, password_hash: str) -> Optional[int]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (email, password_hash)
                VALUES (?, ?)
            ''', (email, password_hash))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        conn.close()
        return dict(user) if user else None
    
    def update_last_login(self, user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET last_login = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
    
    def add_device(self, user_id: int, device_hash: str, device_name: str = None) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as device_count 
                FROM user_devices 
                WHERE user_id = ? AND is_active = 1
            ''', (user_id,))
            
            device_count = cursor.fetchone()['device_count']
            
            if device_count >= 4:
                conn.close()
                return False
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_devices 
                (user_id, device_hash, device_name, last_active)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, device_hash, device_name))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_user_devices(self, user_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_devices 
            WHERE user_id = ? AND is_active = 1
            ORDER BY last_active DESC
        ''', (user_id,))
        
        devices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return devices
    
    def remove_device(self, user_id: int, device_hash: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_devices 
            SET is_active = 0 
            WHERE user_id = ? AND device_hash = ?
        ''', (user_id, device_hash))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def create_subscription(self, user_id: int, plan_type: str, price: float) -> Optional[int]:
        try:
            start_date = datetime.now()
            if plan_type == 'monthly':
                end_date = start_date + timedelta(days=30)
            elif plan_type == 'yearly':
                end_date = start_date + timedelta(days=365)
            else:
                return None
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE subscriptions 
                SET is_active = 0 
                WHERE user_id = ? AND is_active = 1
            ''', (user_id,))
            
            cursor.execute('''
                INSERT INTO subscriptions 
                (user_id, plan_type, price, start_date, end_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, plan_type, price, start_date.isoformat(), end_date.isoformat()))
            
            subscription_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return subscription_id
        except:
            return None
    
    def get_active_subscription(self, user_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM subscriptions 
            WHERE user_id = ? AND is_active = 1 
            AND end_date > CURRENT_TIMESTAMP
            LIMIT 1
        ''', (user_id,))
        
        subscription = cursor.fetchone()
        conn.close()
        
        return dict(subscription) if subscription else None
    
    def check_subscription_valid(self, user_id: int) -> bool:
        subscription = self.get_active_subscription(user_id)
        return subscription is not None
    
    def create_payment(self, user_id: int, amount: float, 
                        subscription_id: int = None) -> Optional[int]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO payments 
                (user_id, subscription_id, amount, status)
                VALUES (?, ?, ?, 'pending')
            ''', (user_id, subscription_id, amount))

            payment_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return payment_id
        except Exception:
            return None
    
    def complete_payment(self, payment_id: int, transaction_id: str):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE payments
            SET status = 'completed',
                payment_date = CURRENT_TIMESTAMP,
                transaction_id = ?
            WHERE id = ?
        ''', (transaction_id, payment_id))

        conn.commit()
        conn.close()

    def create_payment_with_key(self, user_id: int, amount: float,
                                subscription_id: int, activation_key: str) -> Optional[int]:
        try:
            key_expires = datetime.now() + timedelta(hours=24)  # Ключ действителен 24 часа

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO payments
                (user_id, subscription_id, amount, status, activation_key, key_expires)
                VALUES (?, ?, ?, 'pending', ?, ?)
            ''', (user_id, subscription_id, amount, activation_key, key_expires.isoformat()))

            payment_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return payment_id
        except Exception:
            return None

    def activate_license_by_key(self, activation_key: str) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT p.*, s.plan_type, s.end_date
            FROM payments p
            JOIN subscriptions s ON p.subscription_id = s.id
            WHERE p.activation_key = ? AND p.status = 'pending'
            AND p.key_expires > CURRENT_TIMESTAMP
        ''', (activation_key,))

        payment = cursor.fetchone()
        conn.close()

        return dict(payment) if payment else None

    def complete_payment_by_key(self, activation_key: str, transaction_id: str):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE payments
            SET status = 'completed',
                payment_date = CURRENT_TIMESTAMP,
                transaction_id = ?
            WHERE activation_key = ?
        ''', (transaction_id, activation_key))

        conn.commit()
        conn.close()
