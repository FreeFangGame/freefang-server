import events, json

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
		
	@staticmethod
	def vote(headers, game, connection):

		if game.up == Werewolf and headers.sender.role == Werewolf and headers.sender.voted == False:
				
			vt = WerewolfVote(headers.target, headers.sender)
			game.votes.append(vt)
			headers.sender.voted = True
			event = events.Werewolfvoteevent(headers.target, headers.sender)
			pckt = json.dumps(event)
			game.send_packet(pckt, connection)

			if len(game.votes) == len(game.werewolves): # All the werewolves voted
				unanimity = all(i.target == game.votes[0].target for i in game.votes)
				if not unanimity:
					# Wolves fucked up, no kill for them
					pass
				else:
					pass
					
				 
			return 0
		else:
			return 1
		
		

class Vote:
    def __init__(self):
        self.sender = None
        self.target = None

class CitizenVote(Vote):
    def __init__(self):
        super(CitizenVote, self).__init__()
        pass

class WerewolfVote(Vote):
    def __init__(self, target, sender):
        super(WerewolfVote, self).__init__()
        pass
