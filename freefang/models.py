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

	def handle_disconnections(self):
		disconnected_players = [] # Track multiple disconnections at a time
		for player in self.players:
			try:
				player.connection.send(b"")  # Sending empty message to check connection status
			except ConnectionResetError:
				disconnected_players.append(player)

		for player in disconnected_players:
			self.players.remove(player)
			print(f"{player.name} disconnected")

		self.update_player_count()

		
	def gameloop(self):
		# Start game and distribute roles
		print("Game starting")
		self.distribute_roles()

		# Setup I/O channels for select as well as message queue for each player
		inputs = [self.socket] + [i.connection for i in self.players]
		outputs = [i.connection for i in self.players]
		msgqueues = {}

		self.handle_disconnections()
		
		while len(self.villagers) > 0 and len(self.werewolves) > 0: # Game should go on as long as there are villagers and werewolves
			read, write, exceptional = select.select(inputs, outputs, inputs)
