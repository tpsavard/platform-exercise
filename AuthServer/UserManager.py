import sqlite3
import uuid
import codecs
import hashlib
import os

# Manages the persistance of user data
class UserManager:

    def __init__(self, db):
        self.db = db


    # Query Methods

    def create_user(self, name, email, password):
        # Check for the existence of the user
        cursor = self.db.cursor()
        cursor.execute('SELECT COUNT(*) FROM Users WHERE Email = ?', (email, ))

        result = cursor.fetchone()
        if result is None:
            raise Exception('Unabled to verify if the user already exists')
        (count, ) = result

        if count > 0:
            raise Exception('User ' + email + ' already exists')

        # Insert the new user
        salt = self.get_new_salt()
        hashedPassword = self.hash_password(password, salt)
        cursor.execute('''
            INSERT INTO 
                Users 
            VALUES 
                (?, ?, ?, ?)''',
            (name, email, hashedPassword, salt))

        self.db.commit()
    
    def validate_credentials(self, email, password):
        # Check for the existence of the user
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM Users WHERE Email = ?', (email, ))
        
        result = cursor.fetchone()
        if result is None:
            return False
        (_, _, dbPassword, salt) = result

        # Validate the password
        hashedPassword = self.hash_password(password, salt)
        return hashedPassword == dbPassword

        return False

    def update_user(self, name, email, password):
        pass

    def delete_user(self, email):
        pass


    # Utility Methods

    def get_new_salt(self):
        return codecs.encode(os.urandom(32), 'hex')

    def hash_password(self, password, salt):
        passwordBytes = password.encode('utf-8')
        saltBytes = codecs.decode(salt, 'hex')
        derived_key = hashlib.pbkdf2_hmac('sha256', passwordBytes, saltBytes, 100000)
        return codecs.encode(derived_key, 'hex')