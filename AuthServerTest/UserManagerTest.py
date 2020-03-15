import unittest
import sqlite3
from AuthServer.UserManager import UserManager

class UserManagerTest(unittest.TestCase):

    def setup_db(self):
        db = sqlite3.connect(':memory:')
        cursor = db.cursor()
        cursor.execute('CREATE TABLE Users (Name TEXT, Email TEXT, PasswordHash TEXT, PasswordSalt TEXT);')
        cursor.execute('''
            INSERT INTO 
                Users 
            VALUES (
                'alice',
                'alice@foo.bar',
                '94f31a148026c638fe8fde6097dbf1d2e90b61be2240c0d57f8acd91a0642626',
                '1112131415161718a1a2a3a4a5a6a7a8'
            )''')
        db.commit()
        return db

    def test_create_validate_user(self):
        userManager = UserManager(self.setup_db())
        userManager.create_user('bob', 'bob@foo.bar', 'password')
        self.assertTrue(userManager.validate_credentials('bob@foo.bar', 'password'))

    def test_create_user_fail_user_exists_already(self):
        userManager = UserManager(self.setup_db())
        with self.assertRaises(Exception):
            userManager.create_user('alice', 'alice@foo.bar', 'password')
    
    def test_validate_credentials_pass(self):
        userManager = UserManager(self.setup_db())
        self.assertTrue(userManager.validate_credentials('alice@foo.bar', 'password'))

    def test_validate_credentials_fail_bad_user(self):
        userManager = UserManager(self.setup_db())
        self.assertFalse(userManager.validate_credentials('bob@foo.bar', 'password'))

    def test_validate_credentials_fail_bad_password(self):
        userManager = UserManager(self.setup_db())
        self.assertFalse(userManager.validate_credentials('alice@foo.bar', 'badpassword'))

if __name__ == '__main__':
    unittest.main()