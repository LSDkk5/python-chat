#!/usr/bin/python

from socket import socket, error, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from platform import system
import config.CLIENT_CONFIG as cc
from threading import Thread
from datetime import datetime
from select import select
import sys
import errno
import ssl

class ChatClient():
    def __init__(self):
        self.__HEADER_LENGTH = cc.HEADER_LENGHT
        self.__server_addr = (cc.ADDRES, cc.PORT)
        self.__connection = socket(AF_INET, SOCK_STREAM)
        self.__connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        if cc.SECURE_CONNECTION:
            self.__ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.__ssl_context.check_hostname = False
            self.__ssl_context.load_verify_locations(cc.PUBLIC_KEY_PATH)
            
            self.__connection = ssl.wrap_socket(self.__connection)

        self.__connection.connect(((self.__server_addr[0], self.__server_addr[1])))
        self.__connection.setblocking(False)
        self.__my_username = cc.NICKNAME

        self.run()

    def run(self):
        if self.__connection:
            print("Welcome, type '{exit}' to left from the chat!")
        username = self.__my_username.encode('utf-8')
        username_header = f"{len(username):<{self.__HEADER_LENGTH}}".encode('utf-8')
        self.__connection.send(username_header + username)
        Thread(target=self.send_message).start()

        while True:
            try:
                username_header = self.__connection.recv(self.__HEADER_LENGTH)
                self.receive_message(username_header)
                if not len(username_header):
                    print('Connection closed by the server\n')
                    sys.exit()
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    #print(f"Reading error: {str(e)}")
                    sys.exit()
            except Exception as e:
                #print(f"Reading error: {str(e)}")
                sys.exit()
                continue
    
    def send_message(self):
        while True:
            message = input(f'{self.__my_username} > ')
            if message == ' ':
                pass
            if message == '{exit}':
                print("You left from the server!")
                self.__connection.close()
                break
            if message:
                self.message_header = f"{len(message):<{self.__HEADER_LENGTH}}".encode('utf-8')
                self.__connection.send(self.message_header + message.encode())
            

 
    def receive_message(self, username_header):
        username_lenght = int(username_header.decode('utf-8').strip())
        username = self.__connection.recv(username_lenght).decode('utf-8')
        message_header = self.__connection.recv(self.__HEADER_LENGTH)
        message_lenght = int(message_header.decode('utf-8').strip())
        message = self.__connection.recv(message_lenght).decode('utf-8')
        print(f'{username}: {message} \n')
        
if __name__ == '__main__':
    ChatClient()