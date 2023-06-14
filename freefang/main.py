import socket
import json 
import models
import freefang_utils as utils
import freefang_net as net
import packets
import threading

def create_game(playercap):
	
	# Create game object 
	game = models.WWgame()
	game.playercap = playercap
	
	
	print("Game created")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #For devs only
	game.socket = s
	s.bind(("0.0.0.0", 9999))
	s.listen(playercap)
	while len(game.players) < playercap: #Temporary, for now wait until playercap reached
		con, addr = s.accept()
		packet = net.read_packet(con)
		if not packet: # If no packet is sent we bail out
			con.close()
			continue
		packet = utils.json_to_object(packet)
		if packet.action == "game_join":
			p = models.Player()
			p.name = packet.headers.name
			p.connection = con
			
			game.players.append(p)
			con.send(utils.obj_to_json(packets.Added_to_game(username=packet.headers.name)).encode()) # Send player a packet confirming success
			print(f"{p.name} has joined the game")
		else:
			continue 

	game.gameloop()

def main():
	print("Starting FreeFang server.")
	create_game(4)
	
	
if __name__ == "__main__":
	main()
