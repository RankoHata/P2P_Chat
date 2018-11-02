""" Client implementation of P2P chat system. """

import socket
import json
import threading
import time
import sys
import atexit  # 仍无法解决系统非正常退出

from base import *

# 没有任何防护，通过设置peername，可以冒充任何人
class Client(object):
    """ CLient implementation of P2P chat system.

    Args:    
        - peername:     str                 Peer's name
        - serverhost:   str                 IP
        - serverport:   int                 The port occupied by the TCP socket receiving the message.
        - server_info:  tuple or list       IP and socket port of the server in the P2P network.
    
    Attributes:
        - peerlist:                 dict        All connected peer: {Peer's name: (Peer's ip, Peer's socket port)}
        - handlers:                 dict        {Received message type: The method of processing recvived messages}
        - static_input_mapping:     dict        {Command line arguments that have benn fixed: The method of processing arguments}    
        - dynamic_input_mapping:    dict        {Variable command line arguments: The method of processing arguments}
        - agree:                    variable    three values signal: None: waiting for input; True: accept chat request; False: Refuse chat request.
    """
    def __init__(self, peername=None, serverhost='localhost', serverport=40000, server_info=('localhost', 30000)):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((serverhost, serverport))
        self.socket.listen(100)
        self.server_info = server_info  # 服务器的地址
        self.serverhost, self.serverport = serverhost, serverport
        self.name = peername if peername is not None else ':'.join((serverhost, serverport))
        # example name: 192.168.0.1:30000
        self.peerlist = {}  # 与该client连接的Peer
        self.handlers = {
            CHAT_MESSAGE: self.recv_message,
            CHAT_ACCEPT: self.chat_accept,
            CHAT_REFUSE: self.chat_refuse,
            CHAT_REQUEST: self.chat_request,
            REGISTER_SUCCESS: self.register_success,
            REGISTER_ERROR: self.register_error,
            LISTPEER: self.display_all_peers,
            DISCONNECT: self.disconnect,
        }
        self.static_input_mapping = {
            'register': self.send_register,
            'listpeer': self.send_listpeer,
            'exit network': self.send_exit_network,

            'list connected peer': self.list_connected_peer,

            'yes': self.accept_chat_request,
            'no': self.refuse_chat_request,

            'help': self.input_prompt,
            
            'exit': self.system_exit,
        }
        self.dynamic_input_mapping = {  # 因为通过字符串首部匹配，映射中不能出现包含关系
            'chat request': self.input_chat_request, 
            'chat message': self.input_chat_message,
            'disconnect': self.input_disconnect,
        }
        self.agree = None  # 是否同意chat request
        self.message_format = '{peername}: {message}'
        self.input_prompt_format = '    {cmd:<35} {prompt}'

    def disconnect(self, msgdata):
        """ Processing received messages from peer:
            Disconnect from the peer. """
        peername = msgdata['peername']
        if peername in self.peerlist:
            print('Disconnected from {}'.format(peername))
            del self.peerlist[peername]

    def register_success(self, msgdata):
        """ Processing received message from server:
            Successful registration on the server. """
        print('Register Successful.')
    
    def register_error(self, msgdata):
        """ Processing received message from server:
            Registration failed on the server. """
        print('Register Error.')
    
    def display_all_peers(self, msgdata):  # Only print, not save.
        """ Processing received message from server:
            Output information about all peers that have been registered on the server. """
        print('display all peers:')
        # print(msgdata['peerlist'])
        for peername, peer_info in msgdata['peerlist'].items():
            print('peername: ' + peername + '---' + peer_info[0] + ':' + str(peer_info[1]))

    def recv_message(self, msgdata):
        """ Processing received chat message from peer."""
        peername = msgdata['peername']
        if peername in self.peerlist:
            print(self.message_format.format(peername=peername, message=msgdata['message']))
            # return self.message_format.format(peername=peername, message=msgdata['message'])
    
    def chat_accept(self, msgdata):
        """ Processing received accept chat request message from peer.
            Add the peer to collection of connected peers. """
        peername = msgdata['peername']
        host = msgdata['host']
        port = msgdata['port']
        print('chat accept: {} --- {}:{}'.format(peername, host, port))
        self.peerlist[peername] = (host, port)  # 会覆盖之间连接的重名的
    
    def chat_refuse(self, msgdata):
        """ Processing received refuse chat request message from peer. """
        print('CHAT REFUSE!')
    
    def chat_request(self, msgdata):
        """ Processing received chat request message from peer. """
        peername = msgdata['peername']
        host, port = msgdata['host'], msgdata['port']
        print('chat_request: {} --- {}:{}'.format(peername, host, port))
        print('Please enter "yes" or "no":')
        # Bug: 之前随意输入的 'yes' or 'no' 会影响后面的判断，实际上该变量与何时收到 chat request 并无实际关联
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
        """ Send a request to server to register peer's information. """
        data = {
            'peername': self.name,
            'host': self.serverhost,
            'port': self.serverport
        }
        socket_send(self.server_info, msgtype=REGISTER, msgdata=data)

    def send_listpeer(self):
        """ Send a request to server to get all peers information. """
        data = {'peername': self.name}
        socket_send(self.server_info, msgtype=LISTPEER, msgdata=data)    
    
    def send_exit_network(self):
        """ Send a request to server to quit P2P network. """
        data = {'peername': self.name}
        socket_send(self.server_info, msgtype=EXIT_NETWORK, msgdata=data)
    
    def send_chat_request(self, host, port):  # 不向服务器注册，也能直接通过host, port连接
        """ Send a chat request to peer. """
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
        """ Send a chat message to peer. """
        try:
            peer_info = self.peerlist[peername]
        except KeyError:
            print('chat message: Peer does not exist.')
        else:
            data = {
                'peername': self.name,
                'message': message
            }
            socket_send(peer_info, msgtype=CHAT_MESSAGE, msgdata=data)
    
    def send_disconnect(self, peername):
        """ Send a disconnect request to peer. """
        try:
            peer_info = self.peerlist[peername]
        except KeyError:
            print('disconnect: Peer does not exist.')
        else:
            data = {'peername': self.name}
            socket_send(peer_info, msgtype=DISCONNECT, msgdata=data)
        

    def list_connected_peer(self):
        """ Output all connected peers information. """
        for peername, peer_info in self.peerlist.items():
            print('peername: ' + peername + '---' + peer_info[0] + ':' + str(peer_info[1]))
    
    def classifier(self, msg):
        """ Scheduling methods. """
        type_ = msg['msgtype']
        data_ = msg['msgdata']
        self.handlers[type_](data_)

    def recv(self):
        """ TCP socket that receives information. """
        while True:
            conn, addr = self.socket.accept()          
            buf = conn.recv(1024)
            msg = json.loads(buf.decode('utf-8'))
            self.classifier(msg)

    def input_chat_request(self, cmd):
        try:
            host, port = cmd.split(' ', maxsplit=3)[-2:]
            port = int(port)  # May throw an ValueError exception.
        except (IndexError, ValueError):
            print('chat request: Arguments Error.')
        else:
            self.send_chat_request(host, int(port))
    
    def input_chat_message(self, cmd):
        try:
            peername, message = cmd.split(' ', maxsplit=3)[-2:]
        except IndexError:
            print('chat message: Arguments Error.')
        else:
            self.send_chat_message(peername, message)
    
    def input_disconnect(self, cmd):
        try:
            peername = cmd.split(' ', maxsplit=1)[-1]
        except IndexError:
            print('disconnect: Arguments Error.')
        else:
            self.send_disconnect(peername)
            if peername in self.peerlist:
                del self.peerlist[peername]

    def accept_chat_request(self):
        self.agree = True
    
    def refuse_chat_request(self):
        self.agree = False
    
    def system_exit(self):  # 若非正常退出，则无法退出网络
        for peername in self.peerlist:  # 断开已连接的Peer
            self.send_disconnect(peername)
        self.send_exit_network()  # 结束程序之前，退出P2P网络，由于程序没有注册flag，所以不论是否注册，都会发送
        sys.exit()
    
    def input_prompt(self):
        print('command list:')
        print(self.input_prompt_format.format(cmd='register', prompt='注册'))
        print(self.input_prompt_format.format(cmd='listpeer', prompt='查看P2P网络内所有Peer'))
        print(self.input_prompt_format.format(cmd='exit network', prompt='退出P2P网络'))
        print(self.input_prompt_format.format(cmd='chat request [host] [port]', prompt='发出聊天请求'))
        print(self.input_prompt_format.format(cmd='chat message [peername] [message]', prompt='发送聊天消息'))
        print(self.input_prompt_format.format(cmd='list connected peer', prompt='查看已连接Peer'))
        print(self.input_prompt_format.format(cmd='help', prompt='查看帮助'))
        print(self.input_prompt_format.format(cmd='disconnect', prompt='断开与Peer的连接'))
        print(self.input_prompt_format.format(cmd='exit', prompt='退出程序'))

    def main(self):
        self.input_prompt()
        while True:
            cmd = input().strip()
            if cmd in self.static_input_mapping:
                self.static_input_mapping[cmd]()
            else:
                flag = False
                for keyword in self.dynamic_input_mapping:
                    if cmd.startswith(keyword):
                        flag = True
                        self.dynamic_input_mapping[keyword](cmd)
                        break
                if flag is False:
                    print('Please enter correct command.')
                    self.input_prompt()

if __name__ == '__main__':
    serverport = int(input('serverport: '))
    peername = input('Your name: ')
    client = Client(peername=peername, serverport=serverport)
    atexit.register(client.system_exit)  # 防止程序意外中断，不能执行系统退出
    t = threading.Thread(target=client.recv)  # 作为子线程启动
    t.setDaemon(True)
    t.start()
    client.main()
