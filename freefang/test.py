import socket
import time
import random
import sys
import json
import traceback
import struct
#names = ["ABCDEFG", "Alice", "Bob", "Malefoy", "Eve", "jjj", "test"]
names = [str(sys.argv[1])]

join_json = """
{{
        "action": "game_join",
        "headers": {{
                "name": "{name}"
        }}
}}
""".format(name=random.choice(names)) # We double the brackets to avoid .format messing things up
ww_json = """
{
	"action": "werewolf_vote",
	"headers": {
		"target": "D"
	}
}
"""
#json = str(len(json)) + "\r" + json
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.connect(("127.0.0.1", 9999))
s.send(struct.pack("<I", len(join_json)) + join_json.encode())
while True:
	leng = struct.unpack("<I", s.recv(4))[0]
	i = s.recv(leng).decode()
	if i:
		role = ""
		try:
			
			jsn = json.loads(i)
			role = jsn["headers"]["role"]
			if role == "Werewolf":
				print("Werewolf")
				s.send(struct.pack("<I", len(ww_json)) + ww_json.encode())
		except Exception as e:
			#traceback.print_exc()
			print(i)
			continue
	print(i)
	
		#s.send((str(len(json)) + "\r").encode())
		#s.send(json.encode())
		#s.recv(4096)
#	s.recv(1024)
