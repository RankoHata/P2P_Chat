import socket
import json

from base import *

# 不接受任何输入，可以把信息放到日志文件里
class Server(object):
    def __init__(self, serverhost='localhost', serverport=30000):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((serverhost, serverport))
        self.socket.listen(100)
        self.peerlist = {}  # 所有已注册的Peer
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
        if peername in self.peerlist:  # 名字重复了，拒绝注册
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
        while True:  # 超过缓冲区大小的，就会丢失信息
            conn, addr = self.socket.accept()  
            buf = conn.recv(1024)
            msg = json.loads(buf.decode('utf-8'))
            self.classifier(msg)


if __name__ == '__main__':
    server = Server()
    print(server.socket)
    server.recv()
