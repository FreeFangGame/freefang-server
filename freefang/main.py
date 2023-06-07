import socket
import json 
import models
import freefang_utils as utils

def create_game(playercap):
	
	# Create game object 
	game = models.WWgame()
	game.playercap = playercap
	
	
	print("Game created")
	players = []
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #For devs only
	game.socket = s
	s.bind(("0.0.0.0", 9999))
	s.listen(playercap)
	while len(game.players) < playercap: #Temporary, for now wait until playercap reached
		con, addr = s.accept()
		cmd = con.recv(1024).decode()
		p = models.Player()
		p.name = utils.randstring()
		p.connection = con
		
		game.players.append(p)
		print(f"{p.name} has joined the game")
	game.gameloop()

		
		
def main():
	print("Starting FreeFang server.")
	create_game(4)
	
	
if __name__ == "__main__":
	main()
