from flask import Blueprint, jsonify, request
from src.models import db
from src.models.login import LoginData # Changed import from User to LoginData
from src.routes.auth import token_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user_id):
    # This route still uses User model, might need adjustment if User model is removed
    # For now, assuming it's for general user info, not authentication data
    users = LoginData.query.all() # Changed to LoginData for consistency
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'Username, email, and password are required'}), 400

    # Check if username or email already exists
    if LoginData.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Username already exists'}), 409
    if LoginData.query.filter_by(username=email).first(): # Assuming email is used as username for login
        return jsonify({'success': False, 'message': 'Email already exists'}), 409

    new_user = LoginData(username=username) # Create LoginData instance
    new_user.set_password(password) # Hash and set password
    # Note: The LoginData model doesn't have an 'email' field directly.
    # If you need to store email in LoginData, you'd extend that model.
    # For now, we're using username as the primary identifier for login.

    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = LoginData.query.get_or_404(user_id) # Changed to LoginData
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = LoginData.query.get_or_404(user_id) # Changed to LoginData
    data = request.json
    user.username = data.get('username', user.username)
    # If you want to update password, you'd add logic here
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = LoginData.query.get_or_404(user_id) # Changed to LoginData
    db.session.delete(user)
    db.session.commit()
    return '', 204
