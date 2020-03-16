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

    def test_create_validate_user_pass(self):
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

    def test_update_user_pass(self):
        userManager = UserManager(self.setup_db())
        userManager.update_user('bob', 'alice@foo.bar', 'newpassword')
        self.assertTrue(userManager.validate_credentials('alice@foo.bar', 'newpassword'))

    def test_update_user_pass_name_only(self):
        userManager = UserManager(self.setup_db())
        userManager.update_user('bob', 'alice@foo.bar', None)
        self.assertTrue(userManager.validate_credentials('alice@foo.bar', 'password'))

    def test_update_user_pass_password_only(self):
        userManager = UserManager(self.setup_db())
        userManager.update_user(None, 'alice@foo.bar', 'newpassword')
        self.assertTrue(userManager.validate_credentials('alice@foo.bar', 'newpassword'))

    def test_update_user_fail_user_does_not_exists(self):
        userManager = UserManager(self.setup_db())
        with self.assertRaises(Exception):
            userManager.update_user('bob', 'bob@foo.bar', 'newpassword')
    
    def test_delete_user_pass(self):
        userManager = UserManager(self.setup_db())
        userManager.delete_user('alice@foo.bar')
        self.assertFalse(userManager.validate_credentials('alice@foo.bar', 'password'))

    def test_delete_user_fail_user_does_not_exists(self):
        userManager = UserManager(self.setup_db())
        with self.assertRaises(Exception):
            userManager.delete_user('bob@foo.bar')

if __name__ == '__main__':
    unittest.main()