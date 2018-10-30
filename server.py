import socket
import json
import time

from base import *


class Server(object):
    def __init__(self, serverhost='localhost', serverport=30000):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((serverhost, serverport))
        self.socket.listen(100)
        self.peerlist = {}
        self.handlers = {
            REGISTER: self.register,
            LISTPEER: self.listpeer,
            EXIT_NETWORK: self.exit_network,
        }

    def add_handler(self, signal, func):
        self.handlers[signal] = func

    def exit_network(self, msgdata):
        peername = msgdata['peername']
        if peername in self.peerlist:
            del self.peerlist[peername]

    def register(self, msgdata):
        peername = msgdata['peername']
        host = msgdata['host']
        port = msgdata['port']
        if peername in self.peerlist:
            socket_send((host, port), msgtype=REGISTER_ERROR, msgdata={})
        else:
            self.peerlist[peername] = (host, port)
            socket_send(self.peerlist[peername], msgtype=REGISTER_SUCCESS, msgdata={})

    def listpeer(self, msgdata):  # 只有注册了才能查询
        peername = msgdata['peername']
        if peername in self.peerlist:
            data = {'peerlist': self.peerlist}
            socket_send(self.peerlist[peername], msgtype=LISTPEER, msgdata=data)

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
    server = Server()
    print(server.socket)
    server.recv()
