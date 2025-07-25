from src.models.login import LoginData
from src.models import db

class Presenter:
    def __init__(self, view):
        self.view = view

    def login(self, username, password):
        if not username or not password:
            self.view.show_error("Username and password are required")
            return

        user = LoginData.query.filter_by(username=username).first()

        if not user or user.user_password != password:
            self.view.show_error("Invalid username or password")
            return

        self.view.show_success("Login successful")
