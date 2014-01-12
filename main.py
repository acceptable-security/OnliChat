import websockets, socket, threading

if __name__ == "__main__":
	HOST = ''
	PORT = 7144
	clients = []
	class chatClient(websockets.WebSocketClient):
		def connected(self):
			if self in clients:
				return
			clients.append(self)
		def disconnected(self):
			clients.remove(self)
		def receive(self,text):
			for client in clients:
				client.send(text)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((HOST, PORT))
	s.listen(4)
	lock = threading.Lock()
	print "Started"

	while True: # wait for socket to connect
		# send socket to chatserver and start monitoring
		chatClient(s.accept(), lock).start()
