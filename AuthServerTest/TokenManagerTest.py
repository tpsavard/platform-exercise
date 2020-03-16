import unittest
import time
from AuthServer.TokenManager import TokenManager

class TokenManagerTest(unittest.TestCase):

    def test_create_token_pass(self):
        tokenManager = TokenManager()
        token = tokenManager.create_token('alice@foo.bar')

        self.assertTrue(token is not None)
        self.assertTrue(len(token) > 0)

    def test_lock_release_update_token_pass(self):
        # Setup the tokens
        tokenManager = TokenManager()
        token1 = tokenManager.create_token('alice@foo.bar')

        # Lock the first token
        tokenManager.lock_on_token(token1)

        # Release the first token
        token2 = tokenManager.release_update_token(token1)

        # Lock the second token
        tokenManager.lock_on_token(token2)

        # Release the second token
        token3 = tokenManager.release_update_token(token2)

        self.assertNotEquals(token1, token2)
        self.assertNotEquals(token2, token3)

    def test_lock_on_token_fail_missing_token(self):
        tokenManager = TokenManager()
        with self.assertRaises(Exception):
            tokenManager.lock_on_token('alice@foo.bar')

    def test_lock_on_token_fail_inactive_token(self):
        # Setup and touch the token
        tokenManager = TokenManager(1, 60)
        token1 = tokenManager.create_token('alice@foo.bar')

        tokenManager.lock_on_token(token1)
        token2 = tokenManager.release_update_token(token1)

        # Let the token go inactive for too long
        time.sleep(2)

        # Attempt to reacquire token
        with self.assertRaises(Exception):
            tokenManager.lock_on_token(token2)

    def test_lock_on_token_fail_expired_token(self):
        # Setup the tokens
        tokenManager = TokenManager(1, 2)
        token = tokenManager.create_token('alice@foo.bar')

        # Let the token expire
        time.sleep(3)        

        # Lock the token
        with self.assertRaises(Exception):
            tokenManager.lock_on_token(token)

    def test_release_update_token_fail_missing_token(self):
        tokenManager = TokenManager()
        with self.assertRaises(Exception):
            tokenManager.release_update_token('NotAValidToken')

    def test_release_update_token_fail_not_locked(self):
        # Setup the tokens
        tokenManager = TokenManager()
        token = tokenManager.create_token('alice@foo.bar')

        # Attempt to immediately release the token
        with self.assertRaises(Exception):
            tokenManager.release_update_token(token)

    def test_lock_release_close_token_pass(self):
        # Setup the tokens
        tokenManager = TokenManager()
        token = tokenManager.create_token('alice@foo.bar')

        # Lock the token
        tokenManager.lock_on_token(token)

        # Release the token
        tokenManager.release_close_token(token)

        # Verify the token was released
        with self.assertRaises(Exception):
            tokenManager.release_close_token(token)

    def test_release_close_token_fail_missing_token(self):
        tokenManager = TokenManager()
        with self.assertRaises(Exception):
            tokenManager.release_close_token('NotAValidToken')

    def test_release_close_token_fail_not_locked(self):
        # Setup the tokens
        tokenManager = TokenManager()
        token = tokenManager.create_token('alice@foo.bar')

        # Attempt to immediately release the token
        with self.assertRaises(Exception):
            tokenManager.release_close_token(token)

    def test_lock_delete_user_pass(self):
        # Setup the tokens
        tokenManager = TokenManager()
        token1 = tokenManager.create_token('alice@foo.bar')
        token2 = tokenManager.create_token('alice@foo.bar')
        token3 = tokenManager.create_token('alice@foo.bar')

        # Delete the User
        tokenManager.lock_on_token(token1)
        tokenManager.delete_user('alice@foo.bar')

        # Verify the tokens were released
        with self.assertRaises(Exception):
            tokenManager.release_close_token(token)

    def test_delete_user_fail_missing_user(self):
        tokenManager = TokenManager()
        with self.assertRaises(Exception):
            tokenManager.delete_user('NotAValidUser')

    def test_delete_user_fail_not_locked(self):
        # Setup the tokens
        tokenManager = TokenManager()
        token = tokenManager.create_token('alice@foo.bar')

        # Attempt to immediately release the token
        with self.assertRaises(Exception):
            tokenManager.delete_user('alice@foo.bar')

    def test_get_user_for_token_pass(self):
        # Setup the tokens
        tokenManager = TokenManager()
        token = tokenManager.create_token('alice@foo.bar')

        # Get the user
        user = tokenManager.get_user_for_token(token)

        self.assertEquals(user, 'alice@foo.bar')

    def test_get_user_for_token_fail_missing_token(self):
        tokenManager = TokenManager()
        with self.assertRaises(Exception):
            tokenManager.get_user_for_token('NotAValidToken')

if __name__ == '__main__':
    unittest.main()