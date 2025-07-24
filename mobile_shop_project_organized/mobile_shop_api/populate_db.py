#!/usr/bin/env python3
"""
Script to populate the database with sample login data
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.login import LoginData, db

def populate_database():
    """Populate the database with sample login data"""
    with app.app_context():
        # Clear existing data
        LoginData.query.delete()
        
        # Sample data from the original SQL
        sample_users = [
            {'user_id': 1, 'username': 'root', 'password': 'Xenom2321@@'},
            {'user_id': 2, 'username': 'mohamad', 'password': '1'},
            {'user_id': 3, 'username': 'ali', 'password': 'password123'},
            {'user_id': 4, 'username': 'majd', 'password': '1'},
            {'user_id': 5, 'username': 'hasan', 'password': 'password123'},
            {'user_id': 6, 'username': 'moh', 'password': '1'},
            {'user_id': 7, 'username': 'sara', 'password': '1'},
            {'user_id': 8, 'username': 'dodo', 'password': '1'},
        ]
        
        # Add users to database
        for user_data in sample_users:
            user = LoginData(
                user_id=user_data['user_id'],
                username=user_data['username'],
                user_password=user_data['password']  # Using plain text for now to match original
            )
            db.session.add(user)
        
        # Commit changes
        db.session.commit()
        print(f"Successfully added {len(sample_users)} users to the database")
        
        # Verify the data
        users = LoginData.query.all()
        print("\nUsers in database:")
        for user in users:
            print(f"  ID: {user.user_id}, Username: {user.username}")

if __name__ == '__main__':
    populate_database()

