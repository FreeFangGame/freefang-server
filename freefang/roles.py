class Role:
	def __init__(self):
		self.number = 2 # Number of people with this role


# There should be more roles in the future that will inherit those
class Villager(Role):
	def __init__(self):
		super(Villager, self).__init__()
		pass
		
class Werewolf(Role):
	def __init__(self):
		super(Werewolf, self).__init__()
		pass
