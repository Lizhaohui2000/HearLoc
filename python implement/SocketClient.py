# mic array is the client
import socket
import time
import numpy as np
import json
import struct

class SocketClient:
	def __init__(self, host='192.168.31.86', port=12345):
		self.HOST = host
		self.PORT = port
		self.address = (host, port)
		self.makeConection()
		
	def makeConection(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect(self.address)
		print('Connection successfully created!!')

	def contentByteData(self, data):
		json_data = json.dumps(data) #json.dumps
		# ~ byte_data = bytes(json_data).encode('utf-8') # python 2
		byte_data = bytes(json_data, encoding='utf-8') # python 2
		mlen = len(byte_data)
		return mlen, byte_data

	def sendData(self, data):
		mlen, byte_data = self.contentByteData(data)
		struct_mlen = struct.pack('i', mlen)
		self.sock.send(struct_mlen)
		
		packet_size = 1024
		temp_size = 0
		while temp_size < mlen:
			self.sock.sendall(byte_data[temp_size:(min(mlen, temp_size+packet_size))])
			temp_size += packet_size
			
	def close(self):
		self.sock.close()

	def __del__(self):
		self.sock.close()
		
if __name__ == '__main__':
	socketClient = SocketClient('172.20.10.4', 12345)
	# mlen,_ = socketClient.contentByteData(data)
	# print(mlen)
	while True:
		data = np.random.randint(32767, size=(4, 48000)).tolist() #, dtype='int16'
		time1 = time.time()
		socketClient.sendData(data)
		print("successfully send!")
		time2 = time.time()
		print(time2-time1)
		time.sleep(2)
