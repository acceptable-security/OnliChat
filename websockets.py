import socket, base64,hashlib
import threading
from hashlib import sha1
GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

def computeHash(hash):
	longkey = hash + GUID
	sha1f = sha1()
	sha1f.update(longkey)
	digest = sha1f.digest()
	ticket = base64.b64encode(digest)
	return ticket.strip()



class WebSocketClient(threading.Thread):
	def __init__(self, (socket,address), lock):
		threading.Thread.__init__(self)
		self.socket = socket
		self.address= address
		self.amountToRead = 2048
		self.buffer = ''
		self.data = ''
		self.lock = lock

	def run(self):
		self.lock.acquire()
		self.lock.release()
		print '%s:%s connected.' % self.address
		self.name = "IP" + str(self.address[0])
		first = self.socket.recv(1024)
		start = first.index('Sec-WebSocket-Key: ')
		end = first.index('==')
		key =  first[start+len('Sec-WebSocket-Key: '):end+2].strip()
		hash = computeHash(key)
		self.socket.send("HTTP/1.1 101 Web Socket Protocol Handshake\r\nUpgrade: WebSocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: " + hash + "\r\n\r\n")
		self.connected()
		while True:
	
			data = self.socket.recv(1024)
			
			if not data:
				break
			tope, data = self.decode(data)
			if tope == "text":
				data = ''.join(data)
				self.receive(data)
			elif tope == "end":
				break
			
		self.socket.close()
		print '%s:%s disconnected.' % self.address
		self.disconnected()
		self.lock.acquire()
		self.lock.release()

	def receive(self, text):
		pass

	def send(self, text):
		self.socket.send(self.encode(text))

	def connected(self):
		pass

	def disconnected(self):
		pass

	def encode(self, st):
		rawData = [ord(c) for c in st]

		frameCount = 0
		eframe = []
		eframe.append(129)

		if len(rawData) <= 125:
			eframe.append(len(rawData))
			eframeCount = 2
		elif len(rawData) >= 126 and len(rawData) <= 65535:
			frame.append(126)
			l = len(rawData)
			eframe.append((l >> 8) & 255)
			eframe.append(l & 255)
			eframeCount = 4
		else:
			eframe[1] = 255
			l = len(rawData)
			eframe.append((l >> 56) & 255)
			eframe.append((l >> 48) & 255)
			eframe.append((l >> 40) & 255)
			eframe.append((l >> 32) & 255)
			eframe.append((l >> 24) & 255)
			eframe.append((l >> 16) & 255)
			eframe.append((l >> 8) & 255)
			eframe.append(l & 255)
			frameCount = 10
		  
		reply = []
		for x in xrange(len(eframe)+len(rawData)):
			reply.append(0)

		bLim = 0
		for x in eframe:
			reply[bLim] = chr(x)
			bLim += 1
		for x in rawData:
			reply[bLim] = chr(x)
			bLim += 1

		return ''.join(reply)

	def decode(self, stringStreamIn): # thanks to hfern at stackoverflow for this
		#turn string values into opererable numeric byte values
		byteArray = [ord(character) for character in stringStreamIn]
		opcode = byteArray[0]
		if opcode == 129:
			datalength = byteArray[1] & 127
			indexFirstMask = 2 
			if datalength == 126:
				indexFirstMask = 4
			elif datalength == 127:
				indexFirstMask = 10
			masks = [m for m in byteArray[indexFirstMask : indexFirstMask+4]]
			indexFirstDataByte = indexFirstMask + 4
			decodedChars = []
			i = indexFirstDataByte
			j = 0
			while i < len(byteArray):
				decodedChars.append( chr(byteArray[i] ^ masks[j % 4]) )
				i += 1
				j += 1
			return "text", decodedChars
		elif opcode == 136:
			return "end", ""
		else:
			return "unknown", ""