# P2P_Chat
A chat application for a simple P2P network.

- Programming language: Python 3.7.0

- Use only built-in libraries.

## Example
    serverport: 40000
    Your name: patchouli
    
    command list:
        register                            注册
        listpeer                            查看P2P网络内所有Peer
        exit network                        退出P2P网络
        chat request [host] [port]          发出聊天请求
        chat message [peername] [message]   发送聊天消息
        list connected peer                 查看已连接Peer
        help                                查看帮助
        disconnect                          断开与Peer的连接
        exit                                退出程序
    
    >> register
    
    Register Successful.
    
    >> listpeer
    
    display all peers:
    peername: alice---localhost:4000
    peername: patchouli---localhost:40000
    
    >> chat request localhost 4000
    
    chat accept: alice --- localhost:4000
    
    >> chat message alice Hello, alice.
    
    >> disconnect alice
    
    >> exit

### Update Records

#### 2018-10-30

##### Basic functions have been implemented.

#### 2018-11-05

##### Code optimization.
