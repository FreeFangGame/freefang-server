import select, random
from roles import *

class Player:
	def __init__(self):
		self.role = None
		self.alive = True
		self.name = ""
		self.connection = 0
		self.voted_by = 0 # Number of people who voted for this player
		self.voted = False


class WWgame:
	def __init__(self):
		self.players = []
		self.playercap = 0
		self.werewolves = []
		self.villagers = []
		self.socket = 0
		self.inputs = []
		self.outputs = []
		self.roles = {Villager: 2, Werewolf: 2} # The number of players for each role should be decided by the client upon game creation and should be implemented alongside the protocol
	def distribute_roles(self):
		noroles = [i for i in self.players] # Get all the players and keep track of those with no roles
		print("Distributing roles to players")
		
		# Randomly give each role to the number of players its supposed to be on, 
		for i, x in self.roles.items(): 
			for y in range(x): 
				index = random.randint(0, len(noroles) - 1)
				noroles[index].role = i # Give that role to a random player and remove him from that list
				noroles[index].connection.send(f"You have gotten the role {i.__name__.encode()}\n".encode())# To replace with json
				print(f"Player {noroles[index].name} got role {i.__name__}") 

				noroles.pop(index)
			
	def update_player_count(self):
		num_players = len(self.players)
		print(f"Number of present players: {num_players}")
	
	def remove_player(self, player):
		self.players.remove(player)
		self.inputs.remove(player.connection)
		self.outputs.remove(player.connection)
		print(f"{player.name} disconnected")

	def handle_disconnections(self):
		disconnected_players = [] # Track multiple disconnections at a time
		for player in self.players:
			try:
				player.connection.send(b"")  # Sending empty message to check connection status
			except ConnectionResetError:
				disconnected_players.append(player)

		for player in disconnected_players:
			self.remove_player(player)

		#self.update_player_count()

		
	def gameloop(self):
		# Start game and distribute roles
		print("Game starting")
		self.handle_disconnections()

		self.distribute_roles()

		# Setup I/O channels for select as well as message queue for each player
		self.inputs = [self.socket] + [i.connection for i in self.players]
		self.outputs = [i.connection for i in self.players]
		msgqueues = {}

		self.socket.setblocking(0)
		
		
		while True: # Game should go on as long as there are villagers and werewolves
			#P.S, we should eventually populate self.werewolves and self.villagers so this doesnt have to be an infinite loop
			read, write, exceptional = select.select(self.inputs, self.outputs, self.inputs)
			for i in read:
				cmd = i.recv(4096).decode()
				# Handle command 
				if not cmd:
					continue  # Empty message, keep going.

			for i in write:
				if msgqueues.get(i): # If a message is pending for a player send it to them
					i.sendall(msgqueues[i].encode())
					del msgqueues[i] # No more message needed to send
					
				else:
					continue
			
			for i in exceptional:  
				self.inputs.remove(i)
				self.outputs.remove(i)
				for x in self.players:
					if player.connection == i:
						print(f"{x.name} has left the game")
						self.players.remove(x)
				i.close()
			self.handle_disconnections()
	
				
