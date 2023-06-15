class Added_to_game: #Packet for when a player is added to a game
	def __init__(self, username):
		self.action = "added_to_game"
		self.headers = {
			"username": username
		}

class Role_attributed:
	def __init__(self, role):
		self.action = "role_attributed"
		self.headers = {
			"role": role
		}

class Role_wakeup:
	def __init__(self, role):
		self.action = "role_wakeup"
		self.headers = {
			"role": role
		}

class Time_change:
	def __init__(self, time):
		self.action = "time_change"
		self.headers = {
			"time": time,
		}
# Event for when a werewolf votes, should only be sent to werewolves
class Werewolf_vote:
	def __init__(self, target, sender):
		self.action = "werewolf_vote"
		self.headers = {
			"sender": sender,
			"target": target
		}

class Show_werewolves: # This packet is sent to all werewolves in the beginning of a game to know who other werewolves are
	def __init__(self, werewolves):
		self.action = "show_werewolves"
		self.headers = {
			"werewolves": werewolves,
		}
