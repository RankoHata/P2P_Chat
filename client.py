import socket
import json
import threading
import time

from base import *

# 没有任何防护，通过设置peername，可以冒充任何人
class Client(object):
    def __init__(self, peername=None, serverhost='localhost', serverport=40000, server_info=('localhost', 30000)):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((serverhost, serverport))
        self.socket.listen(100)
        self.server_info = server_info
        self.serverhost, self.serverport = serverhost, serverport
        self.name = peername if peername is not None else ':'.join((serverhost, serverport))
        self.peerlist = {}
        self.handlers = {
            CHAT_MESSAGE: self.recv_message,
            CHAT_ACCEPT: self.chat_accept,
            CHAT_REFUSE: self.chat_refuse,
            CHAT_REQUEST: self.chat_request,
            REGISTER_SUCCESS: self.register_success,
            REGISTER_ERROR: self.register_error,
            LISTPEER: self.display_all_peers,
        }
        self.message_format = '{peername}: {message}'
    
    def register_success(self, msgdata):
        print('Register Successful.')
    
    def register_error(self, msgdata):
        print('Register Error.')
    
    def display_all_peers(self, msgdata):
        print('display all peers:')
        print(msgdata['peerlist'])
        for peername, peer_info in msgdata['peerlist'].items():
            print('peername: ' + peername + '---' + peer_info[0] + ':' + str(peer_info[1]))

    def recv_message(self, msgdata):
        peername = msgdata['peername']
        if peername in self.peerlist:
            print(self.message_format.format(peername=peername, message=msgdata['message']))
            # return self.message_format.format(peername=peername, message=msgdata['message'])
    
    def chat_accept(self, msgdata):
        peername = msgdata['peername']
        host = msgdata['host']
        port = msgdata['port']
        self.peerlist[peername] = (host, port)  # 会覆盖之间连接的重名的
    
    def chat_refuse(self, msgdata):
        print('CHAT REFUSE!')
    
    def chat_request(self, msgdata):
        peername = msgdata['peername']
        host, port = msgdata['host'], msgdata['port']
        opinion = input()
        if opinion[0] == 'y':
            data = {
                'peername': self.name,
                'host': self.serverhost,
                'port': self.serverport
            }
            socket_send((host, port), msgtype=CHAT_ACCEPT, msgdata=data)
            self.peerlist[peername] = (host, port)
        else:
            socket_send((host, port), msgtype=CHAT_REFUSE, msgdata={})
    
    def send_register(self):
        data = {
            'peername': self.name,
            'host': self.serverhost,
            'port': self.serverport
        }
        socket_send(self.server_info, msgtype=REGISTER, msgdata=data)

    def send_listpeer(self):
        data = {'peername': self.name}
        socket_send(self.server_info, msgtype=LISTPEER, msgdata=data)    
    
    def send_chat_request(self, host, port):
        data = {
            'peername': self.name,
            'host': self.serverhost,
            'port': self.serverport
        }
        socket_send((host, port), msgtype=CHAT_REFUSE, msgdata=data)
    
    def send_chat_message(self, peername, message):
        data = {
            'peername': self.name,
            'message': message
        }
        socket_send(self.peerlist[peername], msgtype=CHAT_MESSAGE, msgdata=data)
    
    def classifier(self, msg):
        type_ = msg['msgtype']
        data_ = msg['msgdata']
        self.handlers[type_](data_)

    def recv(self):
        while True:
            conn, addr = self.socket.accept()          
            buf = conn.recv(1024)
            msg = json.loads(buf.decode('utf-8'))
            self.classifier(msg)


def socket_send(address, msgtype, msgdata):
    msg = {'msgtype': msgtype, 'msgdata': msgdata}
    msg = json.dumps(msg).encode('utf-8')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(address)
    s.send(msg)
    s.close()


if __name__ == '__main__':
    serverport = int(input())
    peername = input()
    client = Client(peername=peername, serverport=serverport)
    t = threading.Thread(target=client.recv)
    t.setDaemon(True)
    t.start()
    while True:
        cmd = input().strip()
        if cmd == 'register':
            client.send_register()
        elif cmd == 'listpeer':
            client.send_listpeer()
        elif cmd.startswith('chat request '):
            try:
                host, port = cmd.split(' ', maxsplit=3)[-2:]
            except IndexError:
                pass
            else:
                client.send_chat_request(host, int(port))
        elif cmd.startswith('chat message '):
            try:
                peername, message = cmd.split(' ', maxsplit=3)[-2:]
            except IndexError:
                pass
            else:
                client.send_chat_message(peername, message)

        
