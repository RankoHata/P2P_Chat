""" All message type about P2P network. """

import json
import socket

# --------------------------------------------------
# Message type: client and server

# 注册
# client -> server
REGISTER = 'REGISTER'

# 客户端退出P2P网络，从服务器注销自己 
# client -> server
EXIT_NETWORK = 'EXIT_NETWORK'

# 注册出错
# server -> client
REGISTER_ERROR = 'REGISTER_ERROR'

# 注册成功
# server -> client
REGISTER_SUCCESS = 'REGISTER_SUCCESS'

# 列出已注册的Peer
# (server -> client) or (client -> server)
LISTPEER = 'LISTPEER'

# -------------------------------------------------
# Message type: client and client

# 断开与已连接的Peer的连接
# (client A -> client B) or (client B -> client A)
DISCONNECT = 'DISCONNECT'

# 聊天请求
# client A -> client B
CHAT_REQUEST = 'CHAT_REQUEST'

# 接受聊天请求
# client B -> client A
CHAT_ACCEPT = 'CHAT_ACCEPT'

# 拒绝聊天请求
# client B -> client A
CHAT_REFUSE = 'CHAT_REFUSE'

# 聊天信息
# (client A -> client B) or (client B -> client A)
CHAT_MESSAGE = 'CHAT_MESSAGE'

# --------------------------------------------------
# Base function


def socket_send(address, msgtype, msgdata):
    """ Send JSON serialized data over a new TCP connection. """
    msg = {'msgtype': msgtype, 'msgdata': msgdata}
    msg = json.dumps(msg).encode('utf-8')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(address)
    except ConnectionRefusedError:
        print('连接出错: 请确认对方已开启')
        raise
    else:
        s.send(msg)
    finally:
        s.close()
