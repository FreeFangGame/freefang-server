import socket
import time
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.connect(("127.0.0.1", 9999))
while True:
	print(s.recv(4096).decode())
