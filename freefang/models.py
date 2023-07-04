import select, random, json, traceback, sys, datetime, time, copy
try:
	from freefang.roles import *
	import freefang.net as fn
	import freefang.packets as packets
	import freefang.utils as utils


except ImportError:
	from roles import *
	import net as fn
	import packets
	import utils
	


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

		#Witch stuff
		self.haskilled = 0
		self.hasrevived = 0
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
		self.read = []
		self.write = []
		self.msgqueues = {}
		self.nightroles = [] # Roles that should be woken up at night, in order
		self.up = 0 # The current role which is woken up, 0 if day.
		self.action_to_function = {"werewolf_vote": Werewolf.vote, "town_vote": Villager.vote, "town_message": self.townmessage, "werewolf_message": self.werewolfmessage, "hunter_kill": Hunter.kill, "seer_reveal":Seer.reveal, "protector_protect": Protector.protect, "witch_kill": Witch.kill, "witch_revive": Witch.revive}
		self.votes = []
		self.connections = {} # Dictionnary associating connections to players

		self.roles = {} # The number of players for each role should be decided by the client upon game creation and should be implemented alongside the protocol
		
		self.town_voting_scheme = "absmaj"
		self.werewolf_voting_scheme = "relmaj"
	
	# This function is a shortcut to send a packet and remove the player if the connection is dead
	def send_packet(self, packet, con):
		try:
			fn.send_packet(packet, con)
		except (BrokenPipeError, ConnectionResetError):
			self.remove_player(con)
		
	def distribute_roles(self):
	# Get all the players and keep track of those with no roles
		print("Distributing roles to players")
		roles = copy.deepcopy(self.roles)
		
		# Randomly give each role to the number of players its supposed to be on, 
		for spl in self.players:
			playerrole, _ = random.choice(list(roles.items()))
			roles[playerrole] -= 1
			if roles[playerrole] == 0:
				del roles[playerrole]
			
			spl.role = playerrole
			fn.send_packet(utils.obj_to_json(packets.Role_attributed(role=playerrole.__name__)), spl.connection)
			print(f"Player {spl.name} got role {playerrole.__name__}") 
			
			if spl.iswerewolf():
				self.werewolves.append(spl)
			else:
				self.villagers.append(spl)
			
				
	def townmessage(self, headers, game, connection):

		for i in self.players:
			fn.send_message(headers.sender.name, headers.message, i.connection) # Send it to all players
	
	def werewolfmessage(self, headers, game, connection):

		for i in self.werewolves:
			fn.send_message(headers.sender.name, headers.message, i.connection) # Send it to all werewolves
		
		
			
	def update_player_count(self):
		num_players = len(self.players)
		print(f"Number of present players: {num_players}")
	
	def remove_player(self, i):
		self.inputs.remove(i)
		self.outputs.remove(i)
		self.read.remove(i)
		self.write.remove(i)
		player = self.connections[i]
		self.players.remove(player)
		if player in self.villagers:
			self.villagers.remove(player)
		elif player in self.werewolves:
			self.werewolves.remove(player)
		for spl in self.players:
			self.send_packet(utils.obj_to_json(packets.Player_leave(username=player.name)), spl.connection)

						
		print(f"{player.name} disconnected")
		
	
	# This function checks if the conditions for game end are met
	def game_continues(self):
		return (len(self.werewolves) < len(self.villagers) and len(self.werewolves) > 0)
		
		
	def kill_player(self, player, reason=None):
		
		# If the player is protected we do nothing. 
		if player.protected:
			return 1
		print(player.name + " died")

		
		# If the player died during the night we keep it in a list to notify the other players when the day rises
		# Otherwise we just send the packet right away
		if self.up != 0 and self.up != Hunter:
			self.nightdeaths.append(player)
			return 0
		player.alive = False

		
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

		self.roles[player.role] -= 1
		

	def handle_disconnections(self):
		for player in self.players:
			try:
				fn.send_packet("", player.connection)  # Sending empty message to check connection status
			except:
				self.remove_player(player.connection)
	


		
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
			self.send_packet(string, i.connection)
			
	def sendwerewolves(self, string):
		for i in self.werewolves:
			self.send_packet(string,i.connection)
	def sendrole(self, string, role):
		for i in self.alive:
			if i.role == role:
				self.send_packet(string, i.connection)
				

	def getplayerbyname(self, name):
		return [i for i in self.players if i.name == name][0]
		
	def eventloop(self): 
		end = None
		while not end and len(self.players) > 1: # This loop will eventually be broken, can be while true.
			time.sleep(0.05)

			self.read, self.write, exceptional = select.select(self.inputs, self.outputs, self.inputs)
			for i in self.read: # Check every connection that has sent a message
				try:
						
					packet = fn.read_packet(i)
					if not packet:
						fn.send_packet("", i)

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
					self.remove_player(i)
					


			for i in self.write:
				if self.msgqueues.get(i): # If a message is pending for a player send it to them
					for x in self.msgqueues[i]:
						self.send_packet(x, i)
					del self.msgqueues[i] # No more message needed to send
					
				else:
					continue
			
			for i in exceptional:  
				self.remove_player(i)
	
		
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
				if self.roles[i] > 0:
					self.queueall(utils.obj_to_json(packets.Role_wakeup(role=i.__name__))) # Notify everyone role has woken up
					self.up = i
					# Run the role's wake up event function
					try:
						i.onwakeup(self)
					except:
						pass
					self.eventloop()
			
			# Remove all protections 
			for player in self.players:
				player.protected = None
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
		
		
		


