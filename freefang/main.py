import socket
import json 
try:
	import freefang.models as models
	import freefang.utils as utils
	import freefang.net as net
	import freefang.packets as packets
	import freefang.roles as roles

except ImportError:
	import models
	import utils
	import net
	import packets
	import roles


import uuid
import threading
import select
import time
import struct 
import argparse
import ssl
import os

VERSIONSTR = """
FreeFang Server 0.3.1
Written by @Solirs and @lukakralik
Licensed under AGPLv3.0
Source code at https://github.com/FreeFangGame/freefang-server
"""

def parse_ruleset(ruleset, game):
	if ruleset.town_voting_scheme:
		game.town_voting_scheme = ruleset.town_voting_scheme.strip()
		delattr(ruleset, "town_voting_scheme")
	if ruleset.werewolf_voting_scheme:
		game.werewolf_voting_scheme = ruleset.werewolf_voting_scheme.strip()
		delattr(ruleset, "werewolf_voting_scheme")
	
		
	ret = {}
	for key, value in ruleset.__dict__.items():
		ret[getattr(roles, key)] = value
	game.roles = ret
	

def game_creation_loop(args):
	
	games = {}
	# Create game object 

		
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #For devs only
	s.setblocking(0)
	s.bind((args.addr, args.port))
	s.listen()
	if args.cert and args.key:
		print("SSL is ENABLED.")
		context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
		context.load_cert_chain(args.cert, args.key)
		s = context.wrap_socket(s, server_side=True)
	print(f"Listening on {args.addr}:{args.port}")
	
	inputs = [s]
	outputs = []
	
	connections = {} # Associating connections to players
	
	write = 0
	read = 0
	
	while True:
		time.sleep(0.05)
		read, write, excp = select.select(inputs, outputs, inputs)
		
		for i in read:
			if i is s:
				print("New connection")
				try:
					con, addr = s.accept() # Accept new connection
					con.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
					inputs.append(con) 
					outputs.append(con)
					connections[con] = 0
					con.setblocking(0)
					
				except ssl.SSLError: 
					# SSL related errors may be thrown but they should not be fatal.
					pass
					 

			else:
				try:
					packet = net.read_packet(i)
					if not packet: # If no packet is sent we bail out
						net.send_packet("", i)
						continue
					packet = utils.json_to_object(packet)
					
					# Game creation
					if packet.action == "game_create":
						gameid = str(uuid.uuid4())
						game = models.WWgame()
						game.playercap = packet.headers.playercap
						parse_ruleset(packet.headers.ruleset, game)
	
						for rl in game.roles: 
							if rl.nightrole:
								game.nightroles.append(rl)
							
						games[gameid] = game
						net.send_packet(utils.obj_to_json(packets.Game_created(gameid=gameid)), i) # Send player a packet confirming success
						
						print("New game")
					
					# Game joining
					elif packet.action == "game_join":
						if not games.get(packet.headers.gameid): # If the game for the proposed gameid doesn't exist
							net.send_packet(utils.obj_to_json(packets.Action_failure(error="game_not_found")), i)
						else:
							game = games[packet.headers.gameid]

							if packet.headers.name in [s.name for s in game.players]:
								net.send_failure(i, "name_already_taken")
								continue
								
							p = models.Player()
							p.name = packet.headers.name
							p.connection = i
							connections[i] = p
							p.game = game
							for spl in game.players:
								net.send_packet(utils.obj_to_json(packets.Player_join(username=p.name)), spl.connection)
							game.players.append(p)
							net.send_packet(utils.obj_to_json(packets.Added_to_game(username=packet.headers.name, players=[i.name for i in game.players])), i) # Send player a packet confirming success

							if len(game.players) == game.playercap:

								thread = threading.Thread(target=game.gameloop)
								for i in game.players:
									inputs.remove(i.connection)
									outputs.remove(i.connection)
								del games[packet.headers.gameid]
								thread.start()
					elif packet.action == "pre_game_message":
						sender = connections[i]
						for spl in sender.game.players:
							net.send_message(sender.name, packet.headers.message, spl.connection)
								
				except Exception as e:
					print(e)
					inputs.remove(i)
					outputs.remove(i)
					read.remove(i)
					write.remove(i)
					player = connections[i]
					if player:
						player.game.players.remove(player)
						for spl in player.game.players:
							try:
								net.send_packet(utils.obj_to_json(packets.Player_leave(username=player.name)), spl.connection)
							except:
								continue
					del connections[i]
						
				
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", "--version", help="Show version", action="store_true")

	parser.add_argument("-p", "--port", help="The port for the server to listen on (default: 9999)", type=int, default="9999")
	parser.add_argument("-i", "--addr", help="The address to listen on (default: 0.0.0.0)", type=str, default="0.0.0.0")

	parser.add_argument("-c", "--cert", help="SSL certificate if you choose to use SSL.", type=os.path.abspath, default=None)
	parser.add_argument("-k", "--key", help="SSL key if you choose to use SSL.", type=os.path.abspath, default=None)
	args = parser.parse_args()
	
	if args.version:
		print(VERSIONSTR)
		return

	print("Starting FreeFang server.")


	game_creation_loop(args)
	
	
	
if __name__ == "__main__":
	main()
