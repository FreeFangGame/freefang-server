import socket
import json 
import models
import freefang_utils as utils

def create_game(playercap):
	
	game = models.WWgame()
	game.playercap = playercap
	
	print("Game created")
	players = []
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
	s.bind(("0.0.0.0", 9999))
	s.listen(5)
	while len(players) < playercap: #Temporary
		con, addr = s.accept()
		cmd = con.recv(1024).decode()
		p = models.Player()
		p.name = utils.randstring()
		p.connection = con
		print(f"{p.name} has joined the game")
		players.append(p)
	print("Game starting")
	game.players = players
	
		
		
def main():
	print("Starting FreeFang server.")
	create_game(4)
	
	
if __name__ == "__main__":
	main()
