import select, random, json, traceback, sys, datetime, time
try:
	from freefang.roles import *
	import freefang.freefang_net as fn
	import freefang.packets as packets
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
		self.protected = None # name of the protected player
		self.game = None
	def iswerewolf(self):
		return issubclass(self.role, Werewolf) and self.alive
			


class WWgame:
	def __init__(self):
		self.nightdeaths = []
		self.players = []
		self.alive = []
		self.dead = []
		self.playercap = 0
		self.werewolves = []
		self.villagers = []
		self.socket = 0
		self.inputs = []
		self.outputs = []
		self.msgqueues = {}
		self.nightroles = [] # Roles that should be woken up at night, in order
		self.up = 0 # The current role which is woken up, 0 if day.
		self.action_to_function = {"werewolf_vote": Werewolf.vote, "town_vote": Villager.vote, "town_message": self.townmessage, "werewolf_message": self.werewolfmessage, "hunter_kill": Hunter.kill, "seer_reveal":Seer.reveal, "protect": Protector.protect, "test_event": test_event}
		self.votes = []
		self.connections = {} # Dictionnary associating connections to players

		self.roles = {} # The number of players for each role should be decided by the client upon game creation and should be implemented alongside the protocol
	def distribute_roles(self):
		noroles = [i for i in self.players] # Get all the players and keep track of those with no roles
		print("Distributing roles to players")
		
		# Randomly give each role to the number of players its supposed to be on, 
		for i, x in self.roles.items(): 
			for _ in range(x): 
				index = random.randint(0, len(noroles) - 1)
				noroles[index].role = i # Give that role to a random player and remove him from that list
				fn.send_packet(utils.obj_to_json(packets.Role_attributed(role=i.__name__)), noroles[index].connection)
				print(f"Player {noroles[index].name} got role {i.__name__}") 

				if noroles[index].iswerewolf():
					self.werewolves.append(noroles[index])
				else:
					self.villagers.append(noroles[index])
				
				noroles.pop(index)
				
	def townmessage(self, headers, game, connection):
		msg = packets.ChatMessage(headers.sender.name, headers.message, str(datetime.datetime.now())) # Create message packet
		packet = utils.obj_to_json(msg)
		for i in self.players:
			fn.send_packet(packet, i.connection) # Send it to all players
	
	def werewolfmessage(self, headers, game, connection):
		msg = packets.ChatMessage(headers.sender.name, headers.message, str(datetime.datetime.now())) # Create message packet
		packet = utils.obj_to_json(msg)
		for i in self.werewolves:
			fn.send_packet(packet, i.connection) # Send it to all werewolves
		
		
			
	def update_player_count(self):
		num_players = len(self.players)
		print(f"Number of present players: {num_players}")
	
	def remove_player(self, player):
		self.players.remove(player)
		self.inputs.remove(player.connection)
		self.outputs.remove(player.connection)
		print(f"{player.name} disconnected")
		
	
	# This function checks if the conditions for game end are met
	def game_continues(self):
		return (len(self.werewolves) < len(self.villagers) and len(self.werewolves) > 0)
		
		
	def kill_player(self, player, reason=None):
		# TODO: Maybe add a list to keep track of players that are alive, also add a list of death that happen during each night
		# to notify the players when day rises 
		print(player.name + " died")
		player.alive = False

		
		# If the player died during the night we keep it in a list to notify the other players when the day rises
		# Otherwise we just send the packet right away
		if self.up != 0 and self.up != Hunter:
			self.nightdeaths.append(player)
			return
			
		
		# Notify everyone that player died
		event = packets.Player_death(name=player.name, role=player.role.__name__, reason=reason)
		
		self.sendall(utils.obj_to_json(event))
		
		# Remove player from various lists reserved to living players
		if player in self.werewolves:
			self.werewolves.remove(player)
		else:
			self.villagers.remove(player)
			
		self.alive.remove(player)
		
		# If the dead player is a hunter we need to wait for him to make his kill
		if player.role == Hunter:
			self.up = Hunter
			self.eventloop()
		
		# Add player to list of dead players
		self.dead.append(player)
		

	def handle_disconnections(self):
		disconnected_players = [] # Track multiple disconnections at a time
		for player in self.players:
			try:
				player.connection.send(b"")  # Sending empty message to check connection status
			except:
				disconnected_players.append(player)

		for player in disconnected_players:
			if player.protected:
				player.protected = None

			self.remove_player(player)

		#self.update_player_count()

		
	def isnight(self):
		return self.time == 0
	# Those two functions queue a message to be sent to all players or all wolves during the select loop
	def queueall(self, string): # Send a message to all players
		for i in self.outputs:
			self.msgqueues.setdefault(i, [])
			self.msgqueues[i].append(string)

	def queuewerewolves(self, string): # Send a message to all wolves
		for i in self.werewolves:				
			self.msgqueues.setdefault(i.connection, [])
			self.msgqueues[i.connection].append(string)
				
	# Those two functions instantly send a packet to their destined targets, either all players or all werewolves
	def sendall(self, string):
		for i in self.players:
			fn.send_packet(string,i.connection)
			
	def sendwerewolves(self, string):
		for i in self.werewolves:
			fn.send_packet(string,i.connection)
			

	def getplayerbyname(self, name):
		return [i for i in self.players if i.name == name][0]
		
	def eventloop(self): 
		end = None
		while not end: # This loop will eventually be broken, can be while true.
			time.sleep(0.05)
			self.handle_disconnections()

			read, write, exceptional = select.select(self.inputs, self.outputs, self.inputs)
			for i in read: # Check every connection that has sent a message
				try:
						
					packet = fn.read_packet(i)
					if not packet:
						net.send_packet("", i)

						continue

					try:
						pckt = utils.json_to_object(packet) # Create an object from the packet
						print(pckt.action)
						setattr(pckt.headers, "sender", self.connections[i]) # Add the packet's sender to the object to use it in the event function
						ret = self.action_to_function[pckt.action](pckt.headers, self, i) # Call an event function depending on the packet's action
						if not ret: 
							fn.send_success(i)
						elif ret == 2: # End our loop and go to the next role
							fn.send_success(i)
							
							# Set end to true to end the loop after message sending is done, then break as no more packets are needed
							end = True
							break
						else: # If 1 is returned then something went wrong, the packet is probably bad (for example voting someone who doesnt exist)
							fn.send_failure(i, error=None)
							pass
					except Exception as e:
						traceback.print_exc()
						fn.send_failure(i, error=None)
				except:
					self.inputs.remove(i)
					self.outputs.remove(i)
					player = self.connections[i]
					self.players.remove(player)
					if player in self.villagers:
						self.villagers.remove(player)
					else:
						self.werewolves.remove(player)
					for spl in self.players:
						fn.send_packet(utils.obj_to_json(packets.Player_leave(username=player.name)), spl.connection)

						
					


			for i in write:
				if self.msgqueues.get(i): # If a message is pending for a player send it to them
					for x in self.msgqueues[i]:
						
						fn.send_packet(x, i)
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
		
		# Sort night roles by the order at which they should wake up (see roles.py)
		self.nightroles.sort(key=lambda x: x.order)
		
		self.handle_disconnections()
		self.distribute_roles()
		
		# Create the list of alive players
		self.alive = [i for i in self.players]
		
		for i in self.players:
			self.connections[i.connection] = i
			
		# Send all werewolves the list of werewolves in the game
		werewolvenames = [i.name for i in self.werewolves]
		self.sendwerewolves(utils.obj_to_json(packets.Show_werewolves(werewolves=werewolvenames)))
		

		# Setup I/O channels for select as well as message queue for each player
		self.inputs = [i.connection for i in self.players]
		self.outputs = [i.connection for i in self.players]

		while self.game_continues(): 
			# Game should go on as long as there are villagers and werewolves, keeping the day night cycle
			self.sendall(utils.obj_to_json(packets.Time_change(time="night"))) # Notify everyone night has fallen
			for i in self.nightroles:
				self.queueall(utils.obj_to_json(packets.Role_wakeup(role=i.__name__))) # Notify everyone role has woken up
				self.up = i
				self.eventloop()
			
			self.sendall(utils.obj_to_json(packets.Time_change(time="day"))) # Notify everyone day has risen
			self.up = 0
			self.time = 1


			
			
			# Notify all players of deaths that happened during the night. 
			for death in self.nightdeaths:
				self.kill_player(death)
			self.nightdeaths = []
			self.up = 0
			if not self.game_continues(): # Game ended during the night, we dip
				break
			self.sendall(utils.obj_to_json(packets.Town_Vote_Begin()))


			for player in self.players:
				player.protected = None
				
			self.eventloop()
			
		# The game ends if the loop above is over
		
		print("Game end")
		
		outcome = ""
		# If all werewolves are dead aka villager win, otherwise its a werewolf win
		if len(self.werewolves) == 0:
			outcome = "town_win"
		else:
			outcome = "werewolf_win"
			
		self.sendall(utils.obj_to_json(packets.Game_end(outcome=outcome)))
		
		
		


