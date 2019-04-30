from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import config.SERVER_CONFIG as sc
from threading import Thread
from datetime import datetime
from select import select
import ssl

if sc.SAVE_LOGS:
    now = datetime.now().strftime("%H:%M:%S")
    today = datetime.today()

class Server:
    def __init__(self):
        self.HEADER_LENGTH = sc.HEADER_LENGHT
        self.SERVER = (sc.SERVER_ADDRES, sc.SERVER_PORT)
        self.PUBLIC_KEY = sc.PUBLIC_KEY_PATH
        self.PRIVATE_KEY = sc.PRIVATE_KEY_PATH
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        
        self.clients = {}

        if sc.SECURE_CONNECTION:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.ssl_context.load_cert_chain(self.PUBLIC_KEY, self.PRIVATE_KEY)

            self.server = self.ssl_context.wrap_socket(self.server_socket, server_side=True)
        else: self.server = self.server_socket

        self.server.bind((self.SERVER[0], self.SERVER[1]))
        self.server.listen()
        self.sockets_list = [self.server]

        self.run()

    def run(self):
            print(f'Listening for connections on {self.SERVER[0]}:{self.SERVER[1]}...\n\n')
            while True:
                read_sockets, _, exception_sockets = select(self.sockets_list, [], self.sockets_list)
                for notified_socket in read_sockets:
                    if notified_socket == self.server:
                        client_socket, client_address = self.server.accept()
                        user = self.receive_message(client_socket)
                        if user is False:
                            continue
                        self.sockets_list.append(client_socket)
                        self.clients[client_socket] = user
                        print(f'Accepted new connection from {client_address[0]}:{client_address[1]}, username: {user["data"].decode("utf-8")}')
                        if sc.SAVE_LOGS:
                                try:
                                    file = open(sc.LOG_FILE_PATH, 'a+')
                                    file.write(f'{today} {now} | {client_address[0]}:{client_address[1]}      {user["data"].decode()} has join the chat!\n')
                                finally:
                                    file.close()
                    else:
                        message = self.receive_message(notified_socket)
                        if message is False or message == "{exit}":
                            print('Closed connection from: {}'.format(self.clients[notified_socket]['data'].decode('utf-8')))
                            if sc.SAVE_LOGS:
                                try:
                                    file = open(sc.LOG_FILE_PATH, 'a+')
                                    file.write(f'{today} {now} | {client_address[0]}:{client_address[1]}      {self.clients[notified_socket]["data"].decode()} has left the chat!\n')
                                finally:
                                    file.close()
                            self.sockets_list.remove(notified_socket)
                            del self.clients[notified_socket]
                            continue
                        user = self.clients[notified_socket]
                        print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
                        self.save_message_logs(client_address, user, message)
                        self.brodcast(client_socket, notified_socket, user, message)
                for notified_socket in exception_sockets:
                    self.sockets_list.remove(notified_socket)
                    del self.clients[notified_socket]
            self.server.close()

    def receive_message(self, client_socket):
        try:
            message_header = client_socket.recv(self.HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())
            return {'header': message_header, 'data': client_socket.recv(message_length)}
        except:
            return False

    def brodcast(self, client_socket, notified_socket, user, message):
        for client_socket in self.clients:
            if client_socket != notified_socket:
                client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    if sc.SAVE_LOGS:
        def save_message_logs(self, client_addr, user_data, message_data):
            try:
                file = open(sc.LOG_FILE_PATH, 'a+')
                file.write(f'{today} {now} | {client_addr[0]}:{client_addr[1]}      {user_data["data"].decode()} > {message_data["data"].decode()}\n')
            finally:
                file.close
    
if __name__ == "__main__":
    Server()