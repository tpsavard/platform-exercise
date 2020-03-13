from TokenManager import TokenManager

class RequestHandler:

    def __init__(self):
        self.tokenManager = TokenManager

    def registration_handler(self, name, email, password):
        pass

    def login_handler(self, email, password):
        pass

    def logout_handler(self, token):
        pass

    def update_handler(self, name, email, password, token):
        pass

    def deletetion_handler(self, token):
        pass