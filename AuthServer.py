# Simple HTTP server implementation for token-based authentication

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re

class AuthServer(BaseHTTPRequestHandler):

    # Request Handler Methods

    def do_POST(self):
        # Parse the JSON input
        raw_data = self.rfile.read(int(self.headers['Content-Length']))
        print("Received from client: " + str(raw_data))
        
        input = {}
        try: 
            input = json.loads(raw_data)
        except:
            self.reply_400("Invalid JSON received")
            return

        # Handle the given command
        if self.path == '/register':
            # Validate inputs
            if not ('name' in input and 'email' in input and self.validate_email(input['email']) and 'password' in input and self.validate_password(input['password'])):
                self.reply_400("Missing or invalid input provided for registration")
                return

            # Create the new user
            try:
                print('Registering user ' + input['email'])
                if input['email'] == 'bad@bad.bad':
                    raise Exception
            except:
                self.reply_400('Failed to register user')
                return

            # Generate response
            self.reply_200(None)

        elif self.path == '/login':
            # Validate inputs
            if not ('email' in input and self.validate_email(input['email']) and 'password' in input and self.validate_password(input['password'])):
                self.reply_400("Missing or invalid input provided for login")
                return

            # Login the user
            try:
                print('Logging in user ' + input['email'])
                if input['email'] == 'bad@bad.bad':
                    raise Exception
                token = 'token'
            except:
                self.reply_400('Failed to log in user')
                return

            # Generate response
            self.reply_200({ 'token' : token })

        elif self.path == '/logout':
            # Validate inputs
            if not 'token' in input:
                self.reply_400("Missing token for logout")
                return

            # Log out the user
            try:
                print('Logging out user with token ' + input['token'])
                if input['token'] == 'bad':
                    raise Exception
            except:
                self.reply_400('Failed to log out user')
                return

            # Generate response
            self.reply_200(None)
        
        elif self.path == '/update':
            # Validate inputs
            if not 'token' in input or ('email' in input and not self.validate_email(input['email'])) or ('password' in input and not self.validate_password(input['password'])):
                self.reply_400("Missing or invalid input provided for registration")
                return

            # Update the user
            try:
                print('Updating user with token ' + input['token'])
                if input['token'] == 'bad':
                    raise Exception
                token = 'token2'
            except:
                self.reply_400('Failed to update user')
                return

            # Generate response
            self.reply_200({ 'token' : token })
        
        else:
            self.reply_404()
            
    def do_DELETE(self):
        # Parse the JSON input
        raw_data = self.rfile.read(int(self.headers['Content-Length']))
        print("Received from client: " + str(raw_data))
        
        input = {}
        try: 
            input = json.loads(raw_data)
        except:
            self.reply_400("Invalid JSON received")
            return

        # Handle the given command
        if self.path == '/delete':
            # Validate inputs
            if not 'token' in input:
                self.reply_400("Missing token for logout")
                return

            # Delete user
            try:
                print('Deleting user with token ' + input['token'])
                if input['token'] == 'bad':
                    raise Exception
            except:
                self.reply_400('Failed to delete user')
                return

            # Generate response
            self.reply_200(None)
        
        else:
            self.reply_404()

    
    # Response Methods

    def reply_200(self, body):
        self.send_response(200)
        self.end_headers
        if body is not None:
            self.wfile.write(bytes(json.dumps(body), 'utf8'))

    def reply_400(self, message):
        self.send_response(400)
        self.end_headers
        response = { 'error-message' : message }
        self.wfile.write(bytes(json.dumps(response), 'utf8'))

    def reply_404(self):
        self.send_response(404)
        self.end_headers

    
    # Utility Methods

    def validate_email(self, email):
        # Regex pattern taken from https://emailregex.com
        return re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)

    def validate_password(self, password):
        # Password should be mimimum of 16 characters
        if len(password) < 16:
            return False

        # Password should contain at least one lowercase letter
        if len(re.findall("[a-z]", password)) < 1:
            return False

        # Password should contain at least one uppercase letter
        if len(re.findall("[A-Z]", password)) < 1:
            return False

        # Password should contain at least one (unicode) digit
        if len(re.findall("[\d]", password)) < 1:
            return False

        # Password should contain at least one special character
        if len(re.findall("[,.:;?!@#$%&-_+=]", password)) < 1:
            return False

        return True


# Main application loop

httpd = HTTPServer(('localhost', 8000), AuthServer)
httpd.serve_forever()