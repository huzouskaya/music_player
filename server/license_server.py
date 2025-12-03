from typing import Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database
import hashlib
import jwt
import time
import uuid
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import string
import os
from yoomoney import Quickpay

app = Flask(__name__)
CORS(app)
db = Database()

SECRET_KEY = "music_player_secret_2024"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "vspace.feature@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "SpaceFeature5")

YOOMONEY_RECEIVER = "4100119422569693"

def generate_activation_key() -> str:
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(16))

def send_activation_email(email: str, activation_key: str, plan_type: str):
    """Send activation key via email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = email
        msg['Subject'] = "Ключ активации Music Player Pro"

        body = f"""
        Спасибо за покупку Music Player Pro!

        Ваш план: {plan_type}
        Ключ активации: {activation_key}

        Для активации:
        1. Откройте приложение Music Player Pro
        2. Перейдите в раздел "Оплата" -> "Активация"
        3. Введите этот ключ: {activation_key}

        Ключ действителен в течение 24 часов.

        С уважением,
        Команда Music Player Pro
        """

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, email, text)
        server.quit()

        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def hash_password(password: str) -> str:
    return hashlib.sha256(f"{password}:{SECRET_KEY}".encode()).hexdigest()

def create_token(user_id: int, email: str) -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.now().timestamp() + 86400
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except Exception:
        return None

def generate_server_activation_key() -> str:
    """Генерирует уникальный ключ активации на сервере"""
    return str(uuid.uuid4()).replace('-', '')[:20].upper()  # 20 символов

def generate_client_hash(server_key: str, device_hash: str) -> str:
    """Генерирует хэш для клиента на основе серверного ключа и устройства"""
    combined = f"{server_key}:{device_hash}:{SECRET_KEY}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16].upper()  # 16 символов

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Missing data'}), 400
    
    password_hash = hash_password(password)
    user_id = db.create_user(email, password_hash)
    
    if user_id:
        token = create_token(user_id, email)
        return jsonify({
            'success': True,
            'token': token,
            'user_id': user_id
        })
    else:
        return jsonify({'success': False, 'error': 'Email already exists'}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Missing data'}), 400
    
    user = db.get_user_by_email(email)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    password_hash = hash_password(password)
    if user['password_hash'] != password_hash:
        return jsonify({'success': False, 'error': 'Invalid password'}), 401
    
    db.update_last_login(user['id'])
    
    token = create_token(user['id'], email)
    return jsonify({
        'success': True,
        'token': token,
        'user_id': user['id']
    })

@app.route('/api/check_subscription', methods=['POST'])
def check_subscription():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'valid': False, 'error': 'No token'}), 401
    
    user_data = verify_token(token)
    if not user_data:
        return jsonify({'valid': False, 'error': 'Invalid token'}), 401
    
    user_id = user_data['user_id']
    device_hash = request.json.get('device_hash')
    
    subscription = db.get_active_subscription(user_id)
    if not subscription:
        return jsonify({'valid': False, 'error': 'No active subscription'}), 403
    
    if device_hash:
        devices = db.get_user_devices(user_id)
        device_hashes = [d['device_hash'] for d in devices]
        
        if device_hash not in device_hashes:
            if not db.add_device(user_id, device_hash, "Новое устройство"):
                return jsonify({
                    'valid': False, 
                    'error': 'Device limit reached (max 4)'
                }), 403
    
    return jsonify({
        'valid': True,
        'subscription': {
            'plan_type': subscription['plan_type'],
            'end_date': subscription['end_date'],
            'days_left': (datetime.fromisoformat(subscription['end_date']) - datetime.now()).days
        }
    })

@app.route('/api/create_payment', methods=['POST'])
def create_payment():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'success': False, 'error': 'No token'}), 401

    user_data = verify_token(token)
    if not user_data:
        return jsonify({'success': False, 'error': 'Invalid token'}), 401

    data = request.json
    plan_type = data.get('plan_type')
    device_hash = data.get('device_hash')

    if not device_hash:
        return jsonify({'success': False, 'error': 'Device hash required'}), 400

    amount = data.get('amount', 299.0 if plan_type == 'monthly' else 2490.0)

    if plan_type not in ['monthly', 'yearly']:
        return jsonify({'success': False, 'error': 'Invalid plan type'}), 400

    server_activation_key = generate_server_activation_key()

    client_key = generate_client_hash(server_activation_key, device_hash)

    subscription_id = db.create_subscription(user_data['user_id'], plan_type, amount)
    if not subscription_id:
        return jsonify({'success': False, 'error': 'Subscription creation failed'}), 500

    payment_id = db.create_payment_with_keys(
        user_data['user_id'],
        amount,
        subscription_id,
        server_activation_key,
        client_key
    )

    if payment_id:
        try:
            quickpay = Quickpay(
                receiver=YOOMONEY_RECEIVER,
                quickpay_form="shop",
                targets=f"Music Player Pro - {plan_type} subscription",
                paymentType="AC",
                sum=amount,
                label=f"payment_{payment_id}"
            )

            payment_url = quickpay.redirected_url
            print(f"Payment URL created: {payment_url}")

            user_email = user_data['email']
            plan_name = "Месячная подписка" if plan_type == 'monthly' else "Годовая подписка"

            return jsonify({
                'success': True,
                'payment_id': payment_id,
                'subscription_id': subscription_id,
                'payment_url': payment_url,
                'client_key': client_key,
                'server_key': server_activation_key,
                'amount': amount,
                'message': 'Оплатите и используйте ключ для активации'
            })
        except Exception as e:
            print(f"Payment creation failed: {e}")
            return jsonify({'success': False, 'error': 'Payment gateway error'}), 500
    else:
        return jsonify({'success': False, 'error': 'Payment creation failed'}), 500

@app.route('/api/account_info', methods=['GET'])
def account_info():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'success': False, 'error': 'No token'}), 401
    
    user_data = verify_token(token)
    if not user_data:
        return jsonify({'success': False, 'error': 'Invalid token'}), 401
    
    user_id = user_data['user_id']
    
    user = db.get_user_by_email(user_data['email'])
    subscription = db.get_active_subscription(user_id)
    devices = db.get_user_devices(user_id)
    
    return jsonify({
        'success': True,
        'user': {
            'email': user['email'],
            'created_at': user['created_at'],
            'last_login': user['last_login']
        },
        'subscription': subscription,
        'devices': devices
    })

@app.route('/api/remove_device', methods=['POST'])
def remove_device():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'success': False, 'error': 'No token'}), 401

    user_data = verify_token(token)
    if not user_data:
        return jsonify({'success': False, 'error': 'Invalid token'}), 401

    device_hash = request.json.get('device_hash')
    if not device_hash:
        return jsonify({'success': False, 'error': 'No device hash'}), 400

    success = db.remove_device(user_data['user_id'], device_hash)
    return jsonify({'success': success})

@app.route('/api/activate_license', methods=['POST'])
def activate_license():
    data = request.json
    activation_key = data.get('activation_key')
    device_hash = data.get('device_hash')

    if not activation_key:
        return jsonify({'success': False, 'error': 'Activation key required'}), 400

    payment = db.activate_license_by_key(activation_key)
    if not payment:
        return jsonify({'success': False, 'error': 'Invalid or expired activation key'}), 400

    user_id = payment['user_id']
    subscription_id = payment['subscription_id']

    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE subscriptions
        SET is_active = 1
        WHERE id = ?
    ''', (subscription_id,))

    if device_hash:
        devices = db.get_user_devices(user_id)
        device_hashes = [d['device_hash'] for d in devices]

        if device_hash not in device_hashes:
            db.add_device(user_id, device_hash, "Активировано по ключу")

    db.complete_payment_by_key(activation_key, f"activated_{int(time.time())}")

    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': 'License activated successfully',
        'subscription': {
            'plan_type': payment['plan_type'],
            'end_date': payment['end_date']
        }
    })

@app.route('/api/verify_activation', methods=['POST'])
def verify_activation():
    """Проверяет активацию по клиентскому ключу"""
    data = request.json
    client_key = data.get('activation_key')
    device_hash = data.get('device_hash')

    if not client_key or not device_hash:
        return jsonify({'success': False, 'error': 'Key and device hash required'}), 400

    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT p.*, s.plan_type, s.end_date
        FROM payments p
        LEFT JOIN subscriptions s ON p.subscription_id = s.id
        WHERE p.client_key = ? AND p.status = 'completed'
    ''', (client_key,))

    payment = cursor.fetchone()

    if not payment:
        return jsonify({'success': False, 'error': 'Invalid or unused key'}), 404

    server_key = payment['server_key']
    expected_client_key = generate_client_hash(server_key, device_hash)

    if expected_client_key != client_key:
        return jsonify({'success': False, 'error': 'Key does not match device'}), 403

    end_date = datetime.fromisoformat(payment['end_date']) if payment['end_date'] else None
    if end_date and end_date < datetime.now():
        return jsonify({'success': False, 'error': 'Subscription expired'}), 403

    user_id = payment['user_id']

    devices = db.get_user_devices(user_id)
    device_hashes = [d['device_hash'] for d in devices]

    if device_hash not in device_hashes:
        if len(devices) >= 4:
            return jsonify({'success': False, 'error': 'Device limit reached'}), 403
        db.add_device(user_id, device_hash, "Активировано")

    cursor.execute('''
        UPDATE payments
        SET status = 'activated', activated_at = CURRENT_TIMESTAMP
        WHERE client_key = ?
    ''', (client_key,))

    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': 'Activation successful',
        'subscription': {
            'plan_type': payment['plan_type'],
            'end_date': payment['end_date'],
            'days_left': (end_date - datetime.now()).days if end_date else None
        }
    })

@app.route('/api/payment_webhook', methods=['POST'])
def payment_webhook():
    """Обработчик вебхуков от YooMoney для обновления статуса платежей"""
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'No data'}), 400

        label = data.get('label')
        if not label or not label.startswith('payment_'):
            return jsonify({'status': 'error', 'message': 'Invalid label'}), 400

        payment_id = int(label.replace('payment_', ''))
        amount = float(data.get('amount', 0))
        operation_id = data.get('operation_id')

        if amount <= 0:
            return jsonify({'status': 'error', 'message': 'Invalid amount'}), 400

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cursor.fetchone()

        if not payment:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Payment not found'}), 404

        if abs(payment['amount'] - amount) > 0.01:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Amount mismatch'}), 400

        cursor.execute('''
            UPDATE payments
            SET status = 'completed', payment_date = CURRENT_TIMESTAMP, transaction_id = ?
            WHERE id = ?
        ''', (operation_id, payment_id))

        cursor.execute('''
            UPDATE subscriptions
            SET is_active = 1
            WHERE id = ?
        ''', (payment['subscription_id'],))

        # Send activation email after successful payment
        cursor.execute('''
            SELECT u.email, p.client_key, s.plan_type
            FROM payments p
            JOIN users u ON p.user_id = u.id
            JOIN subscriptions s ON p.subscription_id = s.id
            WHERE p.id = ?
        ''', (payment_id,))

        email_data = cursor.fetchone()
        if email_data:
            user_email, client_key, plan_type = email_data
            plan_name = "Месячная подписка" if plan_type == 'monthly' else "Годовая подписка"
            email_sent = send_activation_email(user_email, client_key, plan_name)
            print(f"Activation email sent to {user_email}: {'Success' if email_sent else 'Failed'}")
        else:
            print(f"Failed to retrieve email data for payment {payment_id}")

        conn.commit()
        conn.close()

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
