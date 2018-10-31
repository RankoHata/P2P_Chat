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
        self.server_info = server_info  # 服务器的地址
        self.serverhost, self.serverport = serverhost, serverport
        self.name = peername if peername is not None else ':'.join((serverhost, serverport))
        self.peerlist = {}  # 与该client连接的Peer
        self.handlers = {
            CHAT_MESSAGE: self.recv_message,
            CHAT_ACCEPT: self.chat_accept,
            CHAT_REFUSE: self.chat_refuse,
            CHAT_REQUEST: self.chat_request,
            REGISTER_SUCCESS: self.register_success,
            REGISTER_ERROR: self.register_error,
            LISTPEER: self.display_all_peers,
        }
        self.input_mapping = {
            'register': self.send_register,
            'listpeer': self.send_listpeer,
            'exit network': self.send_exit_network,
            
            'chat request': self.input_chat_request, 
            'chat message': self.input_chat_message,

            'list connected peer': self.list_connected_peer,

            'yes': self.accept_chat_request,
            'no': self.refuse_chat_request,

            'help': self.input_prompt,

            'exit': self.system_exit
        }
        self.agree = None  # 是否同意chat request
        self.message_format = '{peername}: {message}'
        self.input_prompt_format = '    {cmd:<20} {prompt}'

    def register_success(self, msgdata):
        print('Register Successful.')
    
    def register_error(self, msgdata):
        print('Register Error.')
    
    def display_all_peers(self, msgdata):  # Only print, not save.
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
        print('chat accept: {} --- {}:{}'.format(peername, host, port))
        self.peerlist[peername] = (host, port)  # 会覆盖之间连接的重名的
    
    def chat_refuse(self, msgdata):
        print('CHAT REFUSE!')
    
    def chat_request(self, msgdata):
        peername = msgdata['peername']
        host, port = msgdata['host'], msgdata['port']
        print('chat_request: {} --- {}:{}'.format(peername, host, port))
        print('Please enter "yes" or "no":')
        # Bug: 之前随意输入的 'yes' or 'no' 会影响后面的判断，实际上该变量与chat request 并无实际关联
        while self.agree is None:  # 通过该变量判断命令行输入，最后将其还原
            time.sleep(0.1)
        if self.agree is True:
            self.agree = None
            data = {
                'peername': self.name,
                'host': self.serverhost,
                'port': self.serverport
            }
            socket_send((host, port), msgtype=CHAT_ACCEPT, msgdata=data)
            self.peerlist[peername] = (host, port)
        elif self.agree is False:
            self.agree = None
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
    
    def send_exit_network(self):
        data = {'peername': self.name}
        socket_send(self.server_info, msgtype=EXIT_NETWORK, msgdata=data)
    
    def send_chat_request(self, host, port):  # 不向服务器注册，也能直接通过host, port连接
        info = (host, port)
        if info not in self.peerlist.values():
            data = {
                'peername': self.name,
                'host': self.serverhost,
                'port': self.serverport
            }
            socket_send((host, port), msgtype=CHAT_REQUEST, msgdata=data)
        else:
            print('You have already connected to {}:{}.'.format(host, port))
    
    def send_chat_message(self, peername, message):
        data = {
            'peername': self.name,
            'message': message
        }
        socket_send(self.peerlist[peername], msgtype=CHAT_MESSAGE, msgdata=data)
    
    def list_connected_peer(self):
        for peername, peer_info in self.peerlist.items():
            print('peername: ' + peername + '---' + peer_info[0] + ':' + str(peer_info[1]))
    
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

    def input_chat_request(self):
        try:
            host = input('>> Please enter host: ', end='')
            port = int(input('>> Please enter port: ', end=''))
        except:
            pass
        else:
            self.send_chat_message(host, port)
    
    def input_chat_message(self):
        try:
            peername = input('>> Please enter peer name: ', end='')
            message = input('>> Please enter message: ', end='')
        except:
            pass
        else:
            self.send_chat_message(peername, message)

    def accept_chat_request(self):
        self.agree = True
    
    def refuse_chat_request(self):
        self.agree = False
    
    def system_exit(self):
        exit(1)
    
    def input_prompt(self):
        print('command list:')
        print(self.input_prompt_format.format(cmd='register', prompt='注册'))
        print(self.input_prompt_format.format(cmd='listpeer', prompt='查看P2P网络内所有Peer'))
        print(self.input_prompt_format.format(cmd='exit network', prompt='退出P2P网络'))
        print(self.input_prompt_format.format(cmd='chat request', prompt='发出聊天请求'))
        print(self.input_prompt_format.format(cmd='chat message', prompt='发送聊天消息'))
        print(self.input_prompt_format.format(cmd='list connected peer', prompt='查看已连接Peer'))
        print(self.input_prompt_format.format(cmd='help', prompt='查看帮助'))
        print(self.input_prompt_format.format(cmd='exit', prompt='退出程序'))

    def main(self):
        self.input_prompt()
        while True:
            cmd = input('>> ').strip()
            if cmd in self.input_mapping:
                self.input_mapping[cmd]()
            else:
                print('Please enter correct command.')
                self.input_prompt()

if __name__ == '__main__':
    serverport = int(input('>> serverport: '))
    peername = input('>> Your name: ')
    client = Client(peername=peername, serverport=serverport)
    t = threading.Thread(target=client.recv)  # 作为子线程启动
    t.setDaemon(True)
    t.start()
    client.main()
