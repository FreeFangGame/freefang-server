import socket
import re 

def create_game():
	conns = []
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
	s.bind(("0.0.0.0", 9999))
	s.listen(5)
	while True:
		con = s.accept()
		cmd = con.recv(1024).decode()
			
		
		
def main():
	print("Starting FreeFang server.")
	create_game()
	
	
if __name__ == "__main__":
	main()
