import socket, base64,hashlib, binascii
import threading
from hashlib import sha1
GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
HOST = ''
PORT = 7144
def computeHash(hash):
    longkey = hash + GUID
    print longkey
    sha1f = sha1()
    sha1f.update(longkey)
    ticket = base64.b64encode(sha1f.digest())
    return ticket #base64.b64encode(hashlib.sha1(longkey).digest())
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(4)
clients = [] #list of clients connected
lock = threading.Lock()
print "Connected!"

class chatServer(threading.Thread):
    def __init__(self, (socket,address)):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address= address
    def announce(self,msg):
        for c in clients:
            c.socket.send('\x00' + msg + '\xff')
    def run(self):
        lock.acquire()
        clients.append(self)
        lock.release()
        print '%s:%s connected.' % self.address
        self.name = "IP" + str(self.address[0])
        first = self.socket.recv(1024)
        start = first.index('Sec-WebSocket-Key: ')
        end = first.index('==')
        key =  first[start+len('Sec-WebSocket-Key: '):end+2]
        print first
        print key
        hash = computeHash(key)
        print hash
        self.socket.send("HTTP/1.1 101 Web Socket Protocol Handshake\r\nUpgrade: WebSocket\r\nConnection: Upgrade\r\nWebSocket-Origin: http://" + str(self.address[0])  + ":" + str(self.address[1]) + "\r\nWebSocket-Location: ws://localhost:9876/\r\n status: 404\r\nSec-WebSocket-Accept: " + key + "\r\nWebSocket-Protocol: sample\r\n\r\n")
        while True:
            data = self.socket.recv(1024)
            if not data:
                break
            if data.split(' ')[0] == "!NAME":
                name = str(data.split(' ')[1:])
                self.announce(self.name + ' changed their name to ' + name + '\n')
                self.name = name
            else:
                for c in clients:
                    c.socket.send(self.name + ": " + data)
        self.socket.close()
        print '%s:%s disconnected.' % self.address
        lock.acquire()
        clients.remove(self)
        lock.release()

while True: # wait for socket to connect
    # send socket to chatserver and start monitoring
    chatServer(s.accept()).start()
