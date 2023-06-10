import socket
import time
json = """
{
	"action": "test_event",
	"headers": {
		"target": "jyunlzrkcm"
	}
}
"""
#json = str(len(json)) + "\r" + json
print(json)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.connect(("127.0.0.1", 9999))
while True:
#	print(s.recv(4096).decode())
	s.send((str(len(json)) + "\r").encode())
	s.send(json.encode())
	s.recv(1024)
