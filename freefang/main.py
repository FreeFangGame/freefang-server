import socket
import json 
import models
import freefang_utils as utils
import freefang_net as net
import packets
import uuid
import threading
import select

def game_creation_loop():
	
	games = {}
	# Create game object 

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #For devs only
	s.setblocking(0)
	s.bind(("0.0.0.0", 9999))
	s.listen()
	
	inputs = [s]
	outputs = []
	
	connections = {} # Associating connections to players
	
	
	while True:
		read, write, excp = select.select(inputs, outputs, inputs)
		
		for i in read:
			if i is s:
				print("New connection")
				con, addr = s.accept() # Accept new connection
				inputs.append(con) 
				outputs.append(con)
				connections[con] = 0
				con.setblocking(0)
			else:
				packet = net.read_packet(i)
				if not packet: # If no packet is sent we bail out
					continue
				packet = utils.json_to_object(packet)
				
				# Game creation
				if packet.action == "game_create":
					gameid = str(uuid.uuid4())
					game = models.WWgame()
					game.playercap = packet.headers.playercap
					games[gameid] = game
					net.send_packet(utils.obj_to_json(packets.Game_created(gameid=gameid)), i) # Send player a packet confirming success

					print("New game")
				
				# Game joining
				elif packet.action == "game_join":
					if not games.get(packet.headers.gameid): # If the game for the proposed gameid doesn't exist
						net.send_packet(utils.obj_to_json(packets.Action_failure(error="game_not_found")), i)
					else:
						game = games[packet.headers.gameid]
							
						p = models.Player()
						p.name = packet.headers.name
						p.connection = i
						connections[i] = p
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

				
def main():
	print("Starting FreeFang server.")
	game_creation_loop()
	
	
if __name__ == "__main__":
	main()
