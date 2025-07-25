from flask import Blueprint, jsonify, request
from functools import wraps
from firebase_admin import auth

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    """Decorator to require valid Firebase ID token for protected routes and check email verification"""
    @wraps(f)
    def decorated(*args, **kwargs):
        id_token = request.headers.get('Authorization')
        
        if not id_token:
            return jsonify({'message': 'Firebase ID token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if id_token.startswith('Bearer '):
                id_token = id_token[7:]
            
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            
            # Check if email is verified
            user = auth.get_user(uid)
            if not user.email_verified:
                return jsonify({'message': 'Email not verified'}), 403
            
            return f(uid, *args, **kwargs)
        except Exception as e:
            return jsonify({'message': f'Invalid Firebase ID token: {str(e)}'}), 401
    
    return decorated





