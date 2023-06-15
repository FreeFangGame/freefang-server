import select, random, json
import sys
try:
	from freefang.roles import *
	import freefang.freefang_net as fn
	import freefang.packets
	import freefang.freefang_utils as utils
except ImportError:
	from roles import *
	import freefang_net as fn
	import packets
	import freefang_utils as utils


def test_event(headers, game, connection):
	print("WE'RE COOKING!!")
	print(headers.target)
	print(headers.sender.name)
	return 0
class Player:
	def __init__(self):
		self.role = None
		self.alive = True
		self.name = ""
		self.connection = 0
		self.voted_by = 0 # Number of people who voted for this player
		self.voted = False
		self.time = 0 # 0 = Night, 1 = Day
	def iswerewolf(self):
		return issubclass(self.role, Werewolf)
			


class WWgame:
	def __init__(self):
		self.players = []
		self.playercap = 0
		self.werewolves = []
		self.villagers = []
		self.socket = 0
		self.inputs = []
		self.outputs = []
		self.msgqueues = {}
		self.nightroles = [Werewolf] # Roles that should be woken up at night, in order
		self.up = 0 # The current role which is woken up, 0 if day.
		self.action_to_function = {"werewolf_vote": Werewolf.vote, "test_event": test_event}
		self.votes = []
		self.connections = {} # Dictionnary associating connections to players

		self.roles = {Villager: 3, Werewolf: 1} # The number of players for each role should be decided by the client upon game creation and should be implemented alongside the protocol
	def distribute_roles(self):
		noroles = [i for i in self.players] # Get all the players and keep track of those with no roles
		print("Distributing roles to players")
		
		# Randomly give each role to the number of players its supposed to be on, 
		for i, x in self.roles.items(): 
			for _ in range(x): 
				index = random.randint(0, len(noroles) - 1)
				noroles[index].role = i # Give that role to a random player and remove him from that list
				noroles[index].connection.send(utils.obj_to_json(packets.Role_attributed(role=i.__name__)).encode())# To replace with json
				print(f"Player {noroles[index].name} got role {i.__name__}") 

				if noroles[index].iswerewolf():
					self.werewolves.append(noroles[index])
				else:
					self.villagers.append(noroles[index])
				
				noroles.pop(index)
			
	def update_player_count(self):
		num_players = len(self.players)
		print(f"Number of present players: {num_players}")
	
	def remove_player(self, player):
		self.players.remove(player)
		self.inputs.remove(player.connection)
		self.outputs.remove(player.connection)
		print(f"{player.name} disconnected")
	def kill_player(self, player):
		print(player.name + " died")
		player.alive = False

	def handle_disconnections(self):
		disconnected_players = [] # Track multiple disconnections at a time
		for player in self.players:
			try:
				player.connection.send(b"")  # Sending empty message to check connection status

			except:
				disconnected_players.append(player)

		for player in disconnected_players:
			self.remove_player(player)

		#self.update_player_count()

		
	def isnight(self):
		return self.time == 0
	def queueall(self, string): # Send a message to all players
		for i in self.outputs:
			if self.msgqueues.get(i):
				self.msgqueues[i] += string
			else:
				self.msgqueues[i] = string
	def queuewerewolves(self, string): # Send a message to all wolves
		for i in self.werewolves:				
			if self.msgqueues.get(i.connection):
				self.msgqueues[i.connection] += string
			else:
				self.msgqueues[i.connection] = string
	def getplayerbyname(self, name):
		return [i for i in self.players if i.name == name][0]
		
	def eventloop(self): 
		while True: # This loop will eventually be broken, can be while true.
			self.handle_disconnections()

			read, write, exceptional = select.select(self.inputs, self.outputs, self.inputs)
			for i in read:
				packet = fn.read_packet(i)
				if not packet:
					continue

				try:
					pckt = utils.json_to_object(packet)
					print("object made")
					setattr(pckt.headers, "sender", self.connections[i])
					print(f"Action {pckt.action}")
					if not self.action_to_function[pckt.action](pckt.headers, self, i): # Returns 1 if failure
						i.sendall(b"OK")
					else:
						i.sendall(b"BAD")# Go to except
				except Exception as e:
					print("Error")
					print(e)
					i.sendall(b"ERROR")
						
					
					


			for i in write:
				if self.msgqueues.get(i): # If a message is pending for a player send it to them
					i.sendall(self.msgqueues[i].encode())
					del self.msgqueues[i] # No more message needed to send
					
				else:
					continue
			
			for i in exceptional:  
				self.inputs.remove(i)
				self.outputs.remove(i)
				for x in self.players:
					if x.connection == i:
						print(f"{x.name} has left the game")
						self.players.remove(x)
				i.close()
	
		
	def gameloop(self):
		# Start game and distribute roles
		print("Game starting")
		self.handle_disconnections()

		self.distribute_roles()
		
		for i in self.players:
			self.connections[i.connection] = i

		# Setup I/O channels for select as well as message queue for each player
		self.inputs = [self.socket] + [i.connection for i in self.players]
		self.outputs = [i.connection for i in self.players]

		self.socket.setblocking(0)
		while len(self.werewolves) < len(self.villagers) and len(self.werewolves) > 0: 
			# Game should go on as long as there are villagers and werewolves, keeping the day night cycle
			self.queueall(utils.obj_to_json(packets.Time_change(time="night"))) # Notify everyone night has fallen
			for i in self.nightroles:
				self.queueall(utils.obj_to_json(packets.Role_wakeup(role=i.__name__))) # Notify everyone role has woken up
				self.up = i
				self.eventloop()
				
			
			self.up = 0
			self.time = 1
			self.queueall(utils.obj_to_json(packets.Time_change(time="day"))) # Notify everyone day has risen

			self.eventloop()


