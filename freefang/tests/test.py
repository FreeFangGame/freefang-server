import socket
import time
import random
import sys
import json
import traceback
import struct
#names = ["ABCDEFG", "Alice", "Bob", "Malefoy", "Eve", "jjj", "test"]
names = [str(sys.argv[1])]
gameid = str(sys.argv[2])
werewolf = False

create_json = """
{
	"action": "game_create",
	"headers": {
		"playercap": 5
	}
}
"""
join_json = """
{{
        "action": "game_join",
        "headers": {{
                "name": "{name}",
                "gameid": "{gid}"
        }}
}}
""".format(name=random.choice(names), gid=gameid) # We double the brackets to avoid .format messing things up
ww_json = """
{
	"action": "werewolf_vote",
	"headers": {
		"target": "D"
	}
}
"""

tw_json= """
{
	"action": "town_vote",
	"headers": {
		"target": "A"
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
		
		if werewolf:
			
			print(names[0] + ": " + i)
		role = ""
		try:
			
			jsn = json.loads(i)
			action = jsn.get("action")
			role = jsn.get("headers").get("role")
			
			if role == "Werewolf" and action == "role_attributed":
				werewolf = True
				print("Werewolf")
				s.send(struct.pack("<I", len(ww_json)) + ww_json.encode())
			time = jsn.get("headers").get("time")
			
			if time == "day":
				s.send(struct.pack("<I", len(tw_json)) + tw_json.encode())

		except Exception as e:
			#traceback.print_exc()
#			print(names[0] + ": " + i)
			continue
	
		#s.send((str(len(json)) + "\r").encode())
		#s.send(json.encode())
		#s.recv(4096)
#	s.recv(1024)
