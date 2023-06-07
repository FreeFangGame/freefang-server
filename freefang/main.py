import socket
import json 
import models
import freefang_utils as utils
import threading

def create_game(playercap):
	
	game = models.WWgame()
	game.playercap = playercap
	
	
	print("Game created")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #For testing only
	game.socket = s
	s.bind(("0.0.0.0", 9999))
	s.listen(5)
	while len(game.players) < playercap: #Temporary
		con, addr = s.accept()
		cmd = con.recv(1024).decode()
		p = models.Player()
		p.name = utils.randstring()
		p.connection = con
		
		game.players.append(p)
		print(f"{p.name} has joined the game")
		threading.Thread(target=player_connection, args=(game, p)).start()
	game.gameloop()

def player_connection(game, player):
    while True:
        try:
            cmd = player.connection.recv(1024).decode()
            if not cmd:
                break  # Empty message means the player disconnected

            # Handle player commands as needed

        except ConnectionResetError: # Unexpected disconnection
            break

    game.players.remove(player)
    print(f"{player.name} has left the game")
		
def main():
	print("Starting FreeFang server.")
	create_game(4)
	
	
if __name__ == "__main__":
	main()
