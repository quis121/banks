import os
import sys


from flask import Flask, send_from_directory, request, abort
from flask_cors import CORS
from src.models import db
from src.models.login import LoginData # Import LoginData
import firebase_admin
from firebase_admin import credentials, auth
import json

from src.routes.user import user_bp
from src.routes.auth import auth_bp

# Initialize Firebase Admin SDK
service_account_json_string = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY2")

if service_account_json_string:
    try:
        service_account_info = json.loads(service_account_json_string)
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")
else:
    print("FIREBASE_SERVICE_ACCOUNT_KEY environment variable not set. Firebase Admin SDK not initialized.")

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')

# Get the absolute path to the directory containing this file (src)
src_dir = os.path.dirname(os.path.abspath(__file__))

# Define the database directory path relative to the src directory
database_dir = os.path.join(src_dir, 'database')
os.makedirs(database_dir, exist_ok=True)

# configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(database_dir, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# --- DB Download Endpoint (FOR DEBUGGING ONLY - DO NOT USE IN PRODUCTION) ---
DOWNLOAD_TOKEN = os.getenv('DB_DOWNLOAD_TOKEN', 'download_database_1234') # Use environment variable for token

@app.route('/download_db')
def download_db():
    token = request.args.get('download_database_1234')
    if token != DOWNLOAD_TOKEN:
        abort(403) # Forbidden

    db_path = os.path.join(database_dir, 'app.db')
    if os.path.exists(db_path):
        return send_from_directory(database_dir, 'app.db', as_attachment=True)
    else:
        abort(404) # Not Found
# ---------------------------------------------------------------------------

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(debug=True)
