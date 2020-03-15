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
        if self.get_user_count(email) > 0:
            raise Exception('User ' + email + ' already exists')

        # Insert the new user
        salt = self.get_new_salt()
        hashedPassword = self.hash_password(password, salt)
        cursor = self.db.cursor()
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
        # Check for the existence of the user
        if self.get_user_count(email) < 1:
            raise Exception('User ' + email + ' does not already exists')

        # Update the user
        salt = self.get_new_salt()
        hashedPassword = self.hash_password(password, salt)
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE 
                Users
            SET
                Name = ?, PasswordHash = ?, PasswordSalt = ?
            WHERE 
                Email = ?''',
            (name, hashedPassword, salt, email))

        self.db.commit()

    def delete_user(self, email):
        # Check for the existence of the user
        if self.get_user_count(email) < 1:
            raise Exception('User ' + email + ' does not already exists')

        # Delete the user
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM Users WHERE Email = ?', (email, ))

        self.db.commit()


    # Utility Methods

    def get_user_count(self, email):
        cursor = self.db.cursor()
        cursor.execute('SELECT COUNT(*) FROM Users WHERE Email = ?', (email, ))

        result = cursor.fetchone()
        if result is None:
            raise Exception('Unabled to verify if the user already exists')
        (count, ) = result

        return count
    
    def get_new_salt(self):
        return codecs.encode(os.urandom(32), 'hex')

    def hash_password(self, password, salt):
        passwordBytes = password.encode('utf-8')
        saltBytes = codecs.decode(salt, 'hex')
        derived_key = hashlib.pbkdf2_hmac('sha256', passwordBytes, saltBytes, 100000)
        return codecs.encode(derived_key, 'hex')