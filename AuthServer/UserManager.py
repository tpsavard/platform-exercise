import sqlite3

# Manages the persistance of user data
class UserManager:

    def __init__(self, db):
        self.db = sqlite3.con(db)

    def create_user(self, name, email, password):
        pass
    
    def does_user_exist(self, email, password):
        pass

    def update_user(self, name, email, password):
        pass

    def delete_user(self, email):
        pass