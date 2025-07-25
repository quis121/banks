from src.presenter import Presenter

class View:
    def __init__(self):
        self.presenter = Presenter(self)

    def login(self):
        username = input("Username: ")
        password = input("Password: ")
        self.presenter.login(username, password)

    def show_success(self, message):
        print(f"Success: {message}")

    def show_error(self, message):
        print(f"Error: {message}")
