from flask import Blueprint, jsonify, request
from src.models.login import LoginData, db # Re-adding these imports
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

@auth_bp.route('/login', methods=['POST'])
@auth_bp.route('/login/', methods=['POST']) # Handle trailing slash
def login():
    """Authenticate user against backend DB and check Firebase email verification"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        username = data['username']
        password = data['password']
        
        # Authenticate against your backend database
        user_from_db = LoginData.query.filter_by(username=username).first()
        
        if not user_from_db or not user_from_db.check_password(password): # Use check_password for hashed passwords
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
        
        # If backend DB authentication is successful, check Firebase email verification
        try:
            firebase_user = auth.get_user_by_email(username) # Assuming username is email
            email_verified = firebase_user.email_verified
        except Exception as e:
            # User might not exist in Firebase Auth, or other Firebase error
            print(f"Firebase user check failed for {username}: {e}")
            email_verified = False # Assume not verified or not found in Firebase

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'email_verified': email_verified,
            'user': user_from_db.to_dict() # Include user data from your DB
        }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500
