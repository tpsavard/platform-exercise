# Fender Digital Platform Engineering Challenge

## Overview

AuthServer is a token-based authentication server exposing JSON-based REST APIs, written in Python. It supports 5 APIs in total:
* __User Registration:__ (POST, /register, { "name" : String, "email" : String, "password" : String } -> ()) Adds a new user with the given information. Returns nothing on success, or an error when the user already exists, or when the email or password are malformed.
* __User Login:__ (POST, /login, { "email" : String, "password" : String } -> { "token" : String }) Creates a new session for a user, if the credentials are valid. Returns the token to use on the next session call on success, or an error if the credentials are invalid.
* __User Logout:__ (POST, /logout, { "token" : String } -> ()) Ends the session associated with the given token. Returns nothing on success, or an error if the token is invalid or expired.
* __User Update:__ (POST, /update, { "name" : String, "email" : String, "password" : String, "token" : String } -> { "token" : String }) Updates the user with the supplied name and password. The email cannot be updated, as that acts as the user's account ID; the name and password are updated if they are given. Returns the token to use on the next session call on success, or an error if the values are malformed, the user cannot be found, or if the token is invalid or expired.
* __User Delete:__ (POST, /logout, { "token" : String } -> ()) Deletes the user and logs out all open sessions for that user. Returns nothing on success, or an error if the token is invalid or expired.

Tokens are random UUIDs that are valid for one request against a given session; they are replaced every update request. Mutliple sessions can be opened for a user. Token expire 15 after the last request, or 12 hours after the session is opened. The replacement of tokens after every non-closing request combined with support for HTTPS communications is intended to offer improved security.

User data are persisted to a SQL database (in this case, SQLite), while log-in sessions are maintained in-memory. Login sessions are more easily re-established when the server is restarted, and therefore do not necessarily need to be persisted (making sessions-specific actions slightly better performing). User names and passwords are stored in plain text in the database, but passwords are stored only in hashed form. Passwords are hashed using SHA-256, after being combined with a 32 byte random salt, which is also stored in plain text in the database. 

While the underlying Python server is not multi-threaded (due to limitations with the sqlite3 module), the request handlers is designed to thread-safe. Login, update, logout, and delete requests all lock on a given user, preventing concurrent conflicting actions. 

Python and SQLite were chosen for this solution because everything that needed for the solution was built-in. While this server is not production-ready, it does reflect the desired architecture, and no separate dependencies besides the latest Python3 are required, simplifying demonstration and usage.

## Execution

The server requires 5 arguments to launch:
* The IP address to bind to
* The port to bind to
* The path to the SQLite database file
* The path to the SSL key file
* The path to the SSL cert file

Once the project has been checked out, it can be launched with the following command:  
`python3 -m AuthServer.AuthServer localhost 4443 ./AuthServer.db ./key.pem ./cert.pem`

### Interacting with the Server

Browsers, Postman, or curl can be used to manually interact with the server. Some sample commands are provided below (replace `<token>` with the returned token, where applicable):

```
# Register
curl -k -X POST -H "Content-Type: text/plain" --data '{"name":"alice","email":"alice@foo.bar","password":"1PasswordPassword!"}' https://127.0.0.1:4443/register

# Login
curl -k -X POST -H "Content-Type: text/plain" --data '{"email":"alice@foo.bar","password":"1PasswordPassword!"}' https://127.0.0.1:4443/login

curl -k -X POST -H "Content-Type: text/plain" --data '{"email":"bob@foo.bar","password":"1PasswordPassword!"}' https://127.0.0.1:4443/login

# Logout
curl -k -X POST -H "Content-Type: text/plain" --data '{"token":"<token>"}' https://127.0.0.1:4443/logout

# Update
curl -k -X POST -H "Content-Type: text/plain" --data '{"name":"charlie","email":"alice@foo.bar","password":"1SomeOtherPassword!","token":"<token>"}' https://127.0.0.1:4443/update

# Delete
curl -k -X DELETE -H "Content-Type: text/plain" --data '{"token":"<token>"}' https://127.0.0.1:4443/delete
```

### Running Tests

The unit tests against the TokenManager and UserManager modules can be executed using following commands:

```
python -m unittest AuthServerTest.TokenManagerTest
python -m unittest AuthServerTest.UserManagerTest
```

## Improvements

With more time, the following improvements could have been made:

* Integration testing, to provide better testing of the server end-to-end. Presently, there is no automated testing of the APIs themselves (through HTTP or otherwise).
* Correct multi-threading support with the HTTP server, to take advantage of and validate the multi-threading support developed.