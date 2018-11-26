""" All message type about P2P network. """

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

# 连接请求
# client A -> client B
REQUEST = 'REQUEST'

# 接受聊天请求
# client B -> client A
CHAT_ACCEPT = 'CHAT_ACCEPT'

# 拒绝聊天请求
# client B -> client A
CHAT_REFUSE = 'CHAT_REFUSE'

# 聊天信息
# (client A -> client B) or (client B -> client A)
CHAT_MESSAGE = 'CHAT_MESSAGE'

# 文件数据传输
# cilent A <-> client B
FILE_TRANSFER = 'FILE_TRANSFER'

# 文件传输请求
# client A -> client B
FILE_TRANSFER_REQUEST = 'FILE_TRANSFER_REQUEST'

# 接受文件请求
# client B -> client A
FILE_TRANSFER_ACCEPT = 'FILE_TRANSFER_ACCEPT'

# 拒绝文件请求
# client B -> client A
FILE_TRANSFER_REFUSE = 'FILE_TRANSFER_REFUSE'
