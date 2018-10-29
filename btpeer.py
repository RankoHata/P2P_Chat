import time
import json
import socket
import threading
import traceback
import logging

logging.basicConfig(level=logging.DEBUG)


# class BTPeer(object):
#     def __init__(self, serverhost, serverport, myid=None):
#         self.serverhost = serverhost
#         self.serverport = serverport
#         self.myid = myid if myid is not None else ':'.join((str(serverhost), str(serverport)))
#         self.peerlock = threading.Lock()
#         self.peers = {}
#         self.handlers = {}
#         self.shutdown = False
#         self.router = None
    
#     def make_server_socket(self, port, backlog=5):
#         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         s.bind(('', port))
#         s.listen(backlog)
#         return s

#     def send2peer(self, peerid, msgtype, msgdata):
#         if self.router:
#             pid, host, port = self.router(pid)
#             if pid is not None:
#                 return self.connect_and_send(host, port, msgtype, msgdata, pid=pid)
#         return None
    
#     def connect_and_send(self, host, port, msgtype, msgdata, pid=None):
#         pass


class BTPeerConnection(object):
    def __init__(self, peerid, host, port, sock=None):
        self.pid = peerid
        if not sock:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((host, int(port)))
        else:
            self.s = sock

    def __make_msg(self, msgtype, msgdata):
        msg = json.dumps({
            'msgtype': msgtype,
            'msgdata': msgdata
        })
        return msg
    
    def send_data(self, msgtype, msgdata):
        try:
            msg = self.__make_msg(msgtype, msgdata)
            self.s.send(msg)
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
            return False
        return True
    
    def recv_data(self):
        try:
            while True:
                con, add = self.s.accept()
                print(add)
                buf = con.recv(1024)
                break
            msg = json.loads(buf)
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
            return {'msgtype': None, 'msgdata': None}
        else:
            return msg

    def close(self):
        self.s.close()
