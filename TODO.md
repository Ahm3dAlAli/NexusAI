# TODO

- handle incomplete conversations
- add auth and user management
    - allow calls to server only from authorized platform requests
- integrate azure
    - auth
    - use azure openai for chat
    - use azure sql db for storing conversations
    - use bing api for search

- auth flow:
    - if not logged in, redirect to login page
    - don't load conversations or messages if not logged in
    - don't display account card if not logged in
    - add user table to store email, name, and password
    - add non mandatory user id and user relationship to conversation and message tables (no association table)
    - signup: create user in db
    - login: check user in db and redirect to home page
    - logout: clear user in db and redirect to login page
    - use simplest auth logic for now: jwt
