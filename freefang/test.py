import socket
import time
import random

names = ["ABCDEFG", "Alice", "Bob", "Malefoy", "Eve", "jjj", "test"]


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
		"target": "jyunlzrkcm"
	}
}
"""
print(join_json)
#json = str(len(json)) + "\r" + json
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.connect(("127.0.0.1", 9999))
s.send((str(len(join_json)) + "\r" + join_json).encode())
while True:
	i = s.recv(4096).decode()
	if i:
		print(i)
		#s.send((str(len(json)) + "\r").encode())
		#s.send(json.encode())
		#s.recv(4096)
#	s.recv(1024)
