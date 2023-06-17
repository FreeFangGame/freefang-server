try:
    import freefang.freefang_net as fn
    import freefang.packets as packets
    import freefang.freefang_utils as utils
except ImportError:
    import freefang_net as fn
    import packets
    import freefang_utils as utils
	

import json
from operator import attrgetter


class Role:
	def __init__(self):
		self.number = 2 # Number of people with this role


# There should be more roles in the future that will inherit those
class Villager(Role):
	def __init__(self):
		super(Villager, self).__init__()
		pass
	@staticmethod
	def vote(headers, game, connection):

		# Check if time is day and sender hasnt voted yet
		if game.up == 0 and headers.sender.voted == False:
			# Create vote object
			vt = TownVote(game.getplayerbyname(headers.target), headers.sender)
			
			# Cast vote
			game.votes.append(vt)
			
			# Mark sender as already voted
			headers.sender.voted = True
			

			event = packets.Town_vote(target=headers.target, sender=headers.sender.name) # Create a packet indicating a person was voted
			pckt = utils.obj_to_json(event) # Serialize it to json
			game.queueall(pckt) # Send it to everyone
			
			if len(game.votes) == len(game.players): # Everyone voted
				votes = {}
				
				# Gather all votes in a dictionary along with their target
				for i in game.votes:
					votes.setdefault(i.target, 0)
					votes[i.target] += 1
				
				# Get the highest number of votes on a player
				maxvotes = max(votes.values())
				
				# Check if that player is tied with another for the amount of votes he was targeted by
				ties = [key for key, value in votes.items() if value == maxvotes]
				print(ties)
				if len(ties) == 1:
					game.kill_player(ties[0])
					return 2
				else:
					return 2
					
				
			
			

			

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
			event = packets.Werewolf_vote(target=headers.target, sender=headers.sender.name) # Create a packet indicating a person was voted
			pckt = utils.obj_to_json(event) # Serialize it to json
			game.queuewerewolves(pckt) # Send it to all werewolves

			if len(game.votes) == len(game.werewolves): # All the werewolves voted
				unanimity = all(i.target == game.votes[0].target for i in game.votes) 
				if not unanimity: # Check if werewolves voted unanimously
					# Wolves fucked up, no kill for them
					pass
				else:
					# Kill the player that was unanimously voted
					kill = game.getplayerbyname(headers.target)
					game.kill_player(kill)
				# Make all werewolves able to vote again
				for i in game.werewolves:
					i.voted = False
				# Reset game.votes
				game.votes = []
				return 2
					
				 
			return 0
		else:
			return 1
		
		

class Vote:
    def __init__(self, target, sender):
        self.sender = sender
        self.target = target

class TownVote(Vote):
    def __init__(self, target, sender):
        super(TownVote, self).__init__(target, sender)
        pass

class WerewolfVote(Vote):
    def __init__(self, target, sender):
        super(WerewolfVote, self).__init__(target, sender)
        pass
