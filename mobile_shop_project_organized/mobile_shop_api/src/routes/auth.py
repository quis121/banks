from flask import Blueprint, jsonify, request
from src.models.login import LoginData, db
import jwt
import datetime
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Secret key for JWT tokens (in production, use environment variable)
JWT_SECRET = 'your-secret-key-here'

def token_required(f):
    """Decorator to require valid JWT token for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        username = data['username']
        password = data['password']
        
        # Find user in database
        user = LoginData.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
        
        # For now, we'll do plain text comparison since the original data uses plain text
        # In production, you should use hashed passwords
        if user.user_password == password:
            # Generate JWT token
            token = jwt.encode({
                'user_id': user.user_id,
                'username': user.username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, JWT_SECRET, algorithm='HS256')
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'token': token,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token(current_user_id):
    """Verify if the provided token is valid"""
    user = LoginData.query.get(current_user_id)
    if user:
        return jsonify({
            'success': True,
            'message': 'Token is valid',
            'user': user.to_dict()
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404

@auth_bp.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user_id):
    """Get all users (protected route example)"""
    users = LoginData.query.all()
    return jsonify({
        'success': True,
        'users': [user.to_dict() for user in users]
    }), 200

