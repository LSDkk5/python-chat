from socket import socket, error, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import config.CLIENT_CONFIG as cc
from unicurses import *
from threading import Thread
from datetime import datetime
from select import select
import sys
import errno
import ssl

class ChatClient():
    def __init__(self):
        self.HEADER_LENGTH = cc.HEADER_LENGHT
        self.server_addr = (cc.ADDRES, cc.PORT)
        self.connection = socket(AF_INET, SOCK_STREAM)
        self.connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        if cc.SECURE_CONNECTION:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.ssl_context.check_hostname = False
            self.ssl_context.load_verify_locations(cc.PUBLIC_KEY_PATH)
            
            self.connection = ssl.wrap_socket(self.connection)

        self.connection.connect(((self.server_addr[0], self.server_addr[1])))
        self.connection.setblocking(False)
        self.my_username = cc.NICKNAME

        self.stdscr = initscr()
        self.stdscr.scrollok(2)
        self.stdscr.refresh()

        self.run()

    def run(self):
        username = self.my_username.encode('utf-8')
        username_header = f"{len(username):<{self.HEADER_LENGTH}}".encode('utf-8')
        self.connection.send(username_header + username)
        Thread(target=self.send_message).start()

        while True:
            try:
                self.stdscr.refresh()
                username_header = self.connection.recv(self.HEADER_LENGTH)
                self.receive_message(username_header)
                if not len(username_header):
                    stdscr.addnstr('Connection closed by the server\n', -1)
                    sys.exit()
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    #print(f"Reading error: {str(e)}")
                    sys.exit()
            except Exception as e:
                #print(f"Reading error: {str(e)}")
                sys.exit()
                continue
        endwin()
    
    def send_message(self):
        while True:
            self.stdscr.refresh()
            message = self.my_raw_input(8, 0, f'{cc.NICKNAME} > ').lower()
            if message == '{exit}':
                self.connection.close()
                endwin()
                break
            if message:
                self.message_header = f"{len(message):<{self.HEADER_LENGTH}}".encode('utf-8')
                self.connection.send(self.message_header + message)

    def my_raw_input(self, r, c, prompt_string):
        echo() 
        self.stdscr.addstr(r, c, prompt_string)
        self.stdscr.refresh()
        input = self.stdscr.getstr(r, c + len(cc.NICKNAME)+2, 120)
        return input
 
    def receive_message(self, username_header):
        username_lenght = int(username_header.decode('utf-8').strip())
        username = self.connection.recv(username_lenght).decode('utf-8')
        message_header = self.connection.recv(self.HEADER_LENGTH)
        message_lenght = int(message_header.decode('utf-8').strip())
        message = self.connection.recv(message_lenght).decode('utf-8')
        self.stdscr.addnstr(f'{username}: {message} \n', -1)
        self.stdscr.refresh()
        
if __name__ == '__main__':
    ChatClient()