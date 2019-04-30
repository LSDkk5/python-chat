A simple Python chatroom with SSL 
=====================================================

Installation:
-------------
    git clone https://github.com/LSDkk5/python-chat
    pip install -r REQUIREMENTS.txt

For server:
-----------
    python server.py
 All server settings are located in config/SERVER_CONFIG.py

For clients:
------------
    python client.py
 Nickname, addres, port for client app you can set in config/CLIENT_CONFIG.py

Keys generated with:
--------------------
openssl req -new -x509 -days 365 -nodes -out public.pem -keyout private.key
