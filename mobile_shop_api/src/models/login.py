from src.models import db
from werkzeug.security import check_password_hash, generate_password_hash

class LoginData(db.Model):
    __tablename__ = 'login_data'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    user_password = db.Column(db.String(255), nullable=False)  # Increased length for hashed passwords
    
    def __repr__(self):
        return f'<LoginData {self.username}>'
    
    def set_password(self, password):
        """Hash and set the password"""
        self.user_password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return check_password_hash(self.user_password, password)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username
            # Note: Never include password in the response
        }

