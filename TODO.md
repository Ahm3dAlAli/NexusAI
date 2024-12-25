# TODO

- handle incomplete conversations
- improve server security
    - allow calls to backend only from authorized platform requests (use jwt validation with user query?)
    - if secret key is not set, accept all requests but display warning in console
- add text when hovering over buttons:
    - logout
    - new conversation
- integrate azure
    - auth
    - use azure openai for chat
    - use azure sql db for storing conversations
    - use bing api for search