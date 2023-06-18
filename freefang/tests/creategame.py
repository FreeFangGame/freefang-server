import socket
import time
import random
import sys
import json
import traceback
import struct

create_json = """
{
	"action": "game_create",
	"headers": {
		"playercap": 5
	}
}
"""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.connect(("127.0.0.1", 9999))
s.send(struct.pack("<I", len(create_json)) + create_json.encode())
while True:
	b = s.recv(4)
	x = s.recv(4096)
	if x:
		print(json.loads(x.decode())["headers"]["id"])
		break
		
