from AuthServer.TokenManager import TokenManager
from AuthServer.UserManager import UserManager

# Logic for authentication server requests, supporting creating users, logging them in and out, updating, and deleteing them
class RequestHandler:

    def __init__(self, tokenManager, userManager):
        self.tokenManager = tokenManager
        self.userManager = userManager

    def registration_handler(self, name, email, password):
        self.tokenManager.create_user(email)
        self.userManager.create_user(name, email, password)

    def login_handler(self, email, password):
        if self.userManager.validate_credentials(email, password):
            return self.tokenManager.create_token(email)
        else:
            raise Exception("Invalid credentials provided")

    def logout_handler(self, token):
        self.tokenManager.lock_on_token(token)
        self.tokenManager.release_close_token(token)

    def update_handler(self, name, email, password, token):
        self.tokenManager.lock_on_token(token)
        self.userManager.update_user(name, email, password)
        return self.tokenManager.release_update_token(token)

    def deletetion_handler(self, token):
        self.tokenManager.lock_on_token(token)
        email = self.tokenManager.get_user_for_token(token)
        self.userManager.delete_user(email)
        self.tokenManager.delete_user(email)