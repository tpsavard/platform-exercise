from datetime import datetime, timedelta
from threading import Lock
import uuid

# Manages the lifespan and validation of authentication tokens; supports multiple token per user, and concurrent access to those tokens
class TokenManager:

    __acquisitionTimeout__ = 5 # 5 seconds

    def __init__(self, tokenLifespan = 900, TokenInactiveDuration = 43200):
        self.tokens = {}
        self.users = {}
        self.maxTokenLifespan = timedelta(seconds = tokenLifespan) # Default is 15 minutes
        self.maxTokenInactiveDuration = timedelta(seconds = TokenInactiveDuration) # Default is 12 hours
    

    # Token Action Methods

    def create_token(self, email):
        # Acquire lock on user
        userRecord = self.lock_user(email)

        # Create a new token for the user
        newToken = self.get_new_token()
        newTokenRecord = TokenRecord(newToken, email)
        self.tokens[newToken] = newTokenRecord
        userRecord.tokens.add(newToken)

        # Release the lock
        userRecord.lock.release()

        return newToken

    def lock_on_token(self, token):
        (tokenRecord, _) = self.get_token_user_records(token, False)

        # Acquire lock on the user
        userRecord = self.lock_user(tokenRecord.user)

        # Verify and update the token
        curLifespan = datetime.now() - tokenRecord.created
        curInactiveDuration = datetime.now() - tokenRecord.lastAccessed
        if abs(curLifespan) > self.maxTokenLifespan or abs(curInactiveDuration) > self.maxTokenInactiveDuration or tokenRecord.token != token:
            userRecord.lock.release()
            raise Exception('Token ' + token + ' no longer valid')
        else:
            tokenRecord.lastAccessed = datetime.now()

    def release_update_token(self, token):
        (tokenRecord, userRecord) = self.get_token_user_records(token, True)

        # Update the token, user records
        oldToken = tokenRecord.token
        newToken = self.get_new_token()

        tokenRecord.token = newToken
        del self.tokens[oldToken]
        self.tokens[newToken] = tokenRecord

        userRecord.tokens.remove(oldToken)
        userRecord.tokens.add(newToken)

        # Release the lock on the user
        userRecord.lock.release()

        return newToken

    def release_close_token(self, token):
        (tokenRecord, userRecord) = self.get_token_user_records(token, True)

        # Update the token, user records
        del self.tokens[token]
        userRecord.tokens.remove(token)

        # Release the lock on the user
        userRecord.lock.release()

    def delete_user(self, user):
        # Get user record
        userRecord = self.users.get(user)
        if userRecord is None:
            raise Exception('User ' + user + ' not found')

        # Verify the user is locked
        if not userRecord.lock.locked():
            raise Exception('Token(s) for user ' + user + ' not locked')

        # Delete the token records
        tokensCopy = userRecord.tokens.copy()
        for token in tokensCopy:
            del self.tokens[token]

        # Release the lock on the user, delete the user record
        userRecord.lock.release()
        del self.users[user]

    def get_user_for_token(self, token):
        (tokenRecord, _) = self.get_token_user_records(token, False)
        return tokenRecord.user


    # Utility Methods

    def get_new_token(self):
        return str(uuid.uuid4())

    def get_token_user_records(self, token, verifyLocked):
        # Get token, user records
        tokenRecord = self.tokens.get(token)
        if tokenRecord is None:
            raise Exception('Token ' + token + ' not found')

        userRecord = self.users[tokenRecord.user]

        # Verify the user is locked
        if verifyLocked and not userRecord.lock.locked():
            raise Exception('Token ' + token + ' not locked')

        return (tokenRecord, userRecord)

    def lock_user(self, email):
        # Acquire lock on user
        userRecord = self.users.get(email)

        if userRecord is None:
            userRecord = UserRecord()
            self.users[email] = userRecord

        if not userRecord.lock.acquire(self.__acquisitionTimeout__):
            raise Exception('Failed to get lock for user ' + email)

        # Revalidate user is available, in case the user was deleted while waiting for the lock
        if email not in self.users:
            raise Exception('User ' + email + ' no longer available')

        return userRecord


# Record for a single token, including information on its lifespan
class TokenRecord:

    def __init__(self, token, user):
        self.token = token
        self.user = user
        self.created = datetime.now()
        self.lastAccessed = datetime.now()


# Record for a single user, including the associated tokens and concurrency lock
class UserRecord:

    def __init__(self):
        self.lock = Lock()
        self.tokens = set()
