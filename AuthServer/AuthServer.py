# Simple HTTP server implementation for token-based authentication

import sys
import json
import re
import sqlite3
import ssl
from http.server import HTTPServer, BaseHTTPRequestHandler
from AuthServer.TokenManager import TokenManager
from AuthServer.UserManager import UserManager
from AuthServer.RequestHandler import RequestHandler

class AuthServer(BaseHTTPRequestHandler):

    # Request Handler Methods

    def do_POST(self):
        input = self.parse_input()

        # Handle the given command
        if self.path == '/register':
            try:
                # Get, validate the input
                name = self.get_name(input)
                email = self.get_email(input)
                password = self.get_password(input)

                # Create a new user
                print('Registering user ' + email)
                requestHandler.registration_handler(name, email, password)
                
                # Generate reply
                self.reply_200()

            except Exception as e:
                self.reply_400(e.args[0])

        elif self.path == '/login':
            try:
                # Get, validate the input
                email = self.get_email(input)
                password = self.get_password(input)

                # Login the user
                print('Logging in user ' + email)
                token = requestHandler.login_handler(email, password)

                # Generate reply
                self.reply_200_with_token(token)

            except Exception as e:
                self.reply_400(e.args[0])

        elif self.path == '/logout':
            try:
                # Get, validate the input
                token = self.get_token(input)

                # Logout the user
                print('Logging out user with token ' + token)
                requestHandler.logout_handler(token)

                # Generate reply
                self.reply_200()

            except Exception as e:
                self.reply_400(e.args[0])
        
        elif self.path == '/update':
            try:
                # Get, validate the input
                name = self.get_name(input, False)
                email = self.get_email(input, False)
                password = self.get_password(input, False)
                token = self.get_token(input)

                # Update the user
                print('Updating user with token ' + token)
                token = requestHandler.update_handler(name, email, password, token)
                
                # Generate reply
                self.reply_200_with_token(token)

            except Exception as e:
                self.reply_400(e.args[0])
            
    def do_DELETE(self):
        input = self.parse_input()

        # Handle the given command
        if self.path == '/delete':
            try:
                # Get, validate the input
                token = self.get_token(input)

                # Delete the user
                print('Deleting user with token ' + token)
                requestHandler.deletetion_handler(token)

                # Generate reply
                self.reply_200()

            except Exception as e:
                self.reply_400(e.args[0])

    
    # Response Methods

    def reply_200(self):
        self.send_response(200)
        self.end_headers

    def reply_200_with_token(self, token):
        self.reply_200
        self.wfile.write(bytes(json.dumps({ 'token' : token }), 'utf8'))

    def reply_400(self, message):
        self.send_error(400, message)

    
    # Utility Methods

    def parse_input(self):
        raw_data = self.rfile.read(int(self.headers['Content-Length']))
        print("Received from client: " + str(raw_data))
        
        try: 
            return json.loads(raw_data)
        except:
            return {}

    def get_name(self, input, required = True):
        if 'name' in input:
            return input['name']
        elif required:
            raise Exception('Unable to retrieve name from input')
        else:
            return None

    def get_email(self, input, required = True):
        if 'email' in input:
            email = input['email']

            # Regex pattern taken from https://emailregex.com
            if not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
                raise Exception('Unable to retrieve email from input')

            return email
        elif required:
            raise Exception('Unable to retrieve email from input')
        else:
            return None

    def get_password(self, input, required = True):
        if 'password' in input:
            password = input['password']

            # Password should be mimimum of 16 characters
            if len(password) < 16:
                raise Exception('Unable to retrieve password from input')

            # Password should contain at least one lowercase letter
            if len(re.findall("[a-z]", password)) < 1:
                raise Exception('Unable to retrieve password from input')

            # Password should contain at least one uppercase letter
            if len(re.findall("[A-Z]", password)) < 1:
                raise Exception('Unable to retrieve password from input')

            # Password should contain at least one (unicode) digit
            if len(re.findall("[\d]", password)) < 1:
                raise Exception('Unable to retrieve password from input')

            # Password should contain at least one special character
            if len(re.findall("[,.:;?!@#$%&-_+=]", password)) < 1:
                raise Exception('Unable to retrieve password from input')

            return password
        elif required:
            raise Exception('Unable to retrieve password from input')
        else:
            return None

    def get_token(self, input):
        if 'token' in input:
            return input['token']
        else:
            raise Exception('Unable to retrieve token from input')


# Main application loop

# Validate args
if len(sys.argv) < 6:
    print('Required Args: <host address> <host port> <sqlite file> <SSL key file> <SSL cert file>')
    exit()

hostaddr = sys.argv[1]
hostport = sys.argv[2]
dbfile = sys.argv[3]
keyfile = sys.argv[4]
certfile = sys.argv[5]

# Setup DB connection
db = sqlite3.connect(dbfile)

# Create necessary handler objects
tokenManager = TokenManager()
userManager = UserManager(db)
requestHandler = RequestHandler(tokenManager, userManager)

# Launch the server
server = HTTPServer((hostaddr, int(hostport)), AuthServer)
server.socket = ssl.wrap_socket(server.socket, keyfile = keyfile, certfile = certfile, server_side = True)
server.serve_forever()