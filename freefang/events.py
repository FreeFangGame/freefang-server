class Event:
	def __init__(self):
		self.event = ""

# Event for when a role wakes up
class Wakeupevent(Event):
	def __init__(self, role):
		super(Wakeupevent, self).__init__()
		self.role = role

# Event for when a player dies
class Deathevent(Event):
	def __init__(self, player, cause):
		super(Deathevent, self).__init__()
		self.player = player
		self.cause = cause
		
# Event for when a werewolf votes, should only be sent to werewolves
class Werewolfvoteevent(Event):
	def __init__(self, target, sender):
		super(Werewolfvoteevent, self).__init__()
		self.target = target
		self.sender = sender
