import select, random
from roles import *

class Player:
	def __init__(self):
		self.role = None
		self.alive = True
		self.name = ""
		self.connection = 0

class WWgame:
	def __init__(self):
		self.players = []
		self.playercap = 0
		self.werewolves = []
		self.villagers = []
		self.socket = 0
		self.roles = {Villager: 2, Werewolf: 2}
	def distribute_roles(self):
		noroles = [i for i in self.players] # Get all the players and keep track of those with no roles
		print("Distributing roles to players")
		
		# Randomly give each role to the number of players its supposed to be on, 
		for i, x in self.roles.items(): 
			for y in range(x): 
				index = random.randint(0, len(noroles) - 1)
				noroles[index].role = i # Give that role to a random player and remove him from that list
				noroles[index].connection.send(f"You have gotten the role {i.__name__.encode()}\n".encode())
				print(f"Player {noroles[index].name} got role {i.__name__}") # To replace with json

				noroles.pop(index)
			
			
	def gameloop(self):
		print("Game starting")
		self.distribute_roles()

		inputs = [self.socket] + [i.connection for i in self.players]
		outputs = [i.connection for i in self.players]
		msgqueues = {}
		
	
