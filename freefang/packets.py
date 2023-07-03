class Added_to_game: #Packet for when a player is added to a game
	def __init__(self, username, players):
		self.action = "added_to_game"
		self.headers = {
			"username": username,
			"players": players # List of the players currently in the game
		}

class Player_join:
	def __init__(self, username):
		self.action = "player_join"
		self.headers = {
			"name": username,
		}
class Player_leave:
	def __init__(self, username):
		self.action = "player_leave"
		self.headers = {
			"name": username,
		}

class Game_created:
	def __init__(self, gameid):
		self.action = "game_created"
		self.headers = {
			"id": gameid
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

# Event for when someone votes during the day
class Town_vote:
	def __init__(self, target, sender):
		self.action = "town_vote"
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

# This packet should be sent back to a player after something is done successfully.
# For example if a werewolf sends a vote packet and it is taken into account, then return this packet
class Action_success:
	def __init__(self):
		self.action = "action_success"

# On the flip side this packet should be sent if there was an error processing a packet (i.e werewolf vote sent during the day)
class Action_failure:
	def __init__(self, error):
		self.action = "action_failure"
		self.headers = {
			"error": error
		}
		
class Player_death:
	def __init__(self, name, role, reason):
		self.action = "player_death"
		self.headers = {
			"name": name,
			"role": role,
			"reason": reason
		}
		
class Game_end:
	def __init__(self, outcome):
		self.action = "game_end"
		self.headers = {
			"outcome": outcome
		}

class ChatMessage:
    def __init__(self, sender, message, timestamp):
        self.action = "chat_message"
        self.headers = {
            "sender": sender,
            "message": message,
            "timestamp": timestamp
        }

class SeerReveal:
    def __init__(self, role, name):
        self.action = "seer_role_reveal"
        self.headers = {
			"role": role,
			"name": name
        }
        
class Town_Vote_Begin:
	def __init__(self):
		self.action = "town_vote_begin"

class Check_alive:
	def __init__(self):
		self.action = "check_alive"
	
# This packet is supposed to be sent to the witch upon wakeup to
# Notify them of the players which have died during the night
class Witch_send_dead:
	def __init__(self, players):
		self.action = "witch_send_dead"
		self.dead = players
	