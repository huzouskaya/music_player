from typing import Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database
import hashlib
import jwt
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)
db = Database()

SECRET_KEY = "music_player_secret_2024"

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
    amount = data.get('amount', 100.0 if plan_type == 'monthly' else 1000.0)
    
    if plan_type not in ['monthly', 'yearly']:
        return jsonify({'success': False, 'error': 'Invalid plan type'}), 400
    
    payment_id = db.create_payment(user_data['user_id'], amount)
    
    if payment_id:
        subscription_id = db.create_subscription(
            user_data['user_id'], 
            plan_type, 
            amount
        )
        
        db.complete_payment(payment_id, f"test_tx_{int(time.time())}")
        
        return jsonify({
            'success': True,
            'payment_id': payment_id,
            'subscription_id': subscription_id,
            'message': 'Для теста подписка активирована сразу. В реальной версии здесь будет редирект на оплату.'
        })
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)