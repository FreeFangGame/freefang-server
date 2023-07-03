try:
    import freefang.net as fn
    import freefang.packets as packets
    import freefang.utils as utils
    import freefang.voting as voting
except ImportError:


    import net as fn
    import packets
    import utils
    import voting

import json
from operator import attrgetter


class Role:
	def __init__(self):
		self.number = 2 # Number of people with this role


# There should be more roles in the future that will inherit those
class Villager(Role):
	nightrole = 0
	def __init__(self):
		super(Villager, self).__init__()
		
		pass
	@staticmethod
	def vote(headers, game, connection):
		
		# Get the player object of the target
		target = game.getplayerbyname(headers.target)


		# Check if time is day and sender hasnt voted yet
		# Reminder that game.up = 0 means that its day
		if game.up == 0 and headers.sender.voted == False and headers.sender.alive and target.alive:
			# Create vote object
			vt = TownVote(target, headers.sender)
			
			
			
			# Cast vote
			game.votes.append(vt)
			
			# Mark sender as already voted
			headers.sender.voted = True
			

			event = packets.Town_vote(target=headers.target, sender=headers.sender.name) # Create a packet indicating a person was voted
			pckt = utils.obj_to_json(event) # Serialize it to json
			game.sendall(pckt) # Send it to everyone
			
			if len(game.votes) == len(game.alive): # Everyone voted
				if game.town_voting_scheme == "relmaj":
					voting.relmaj(game)
				elif game.town_voting_scheme == "absmaj":
					voting.absmaj(game)
				return 2

				
			
			

			

class Werewolf(Role):
	nightrole = 1
	order = 3
	def __init__(self):
		super(Werewolf, self).__init__()
		pass
		
	@staticmethod
	def vote(headers, game, connection):
		
		target = game.getplayerbyname(headers.target)

		if game.up == Werewolf and headers.sender.iswerewolf() and headers.sender.voted == False and target.alive and headers.sender.alive:
			if target == headers.sender.protected:
				return 3  # protected player case (3)
			vt = WerewolfVote(target, headers.sender)
			game.votes.append(vt)
			headers.sender.voted = True
			event = packets.Werewolf_vote(target=headers.target, sender=headers.sender.name) # Create a packet indicating a person was voted
			pckt = utils.obj_to_json(event) # Serialize it to json
			game.sendwerewolves(pckt) # Send it to all werewolves

			if len(game.votes) == len(game.werewolves): # All the werewolves voted
				if game.werewolf_voting_scheme == "unanimity":
					voting.unanimity(game)
				elif game.werewolf_voting_scheme == "relmaj":
					voting.relmaj(game)
				elif game.werewolf_voting_scheme == "absmaj":
					voting.absmaj(game)
				for i in game.werewolves:
					i.voted = False
				return 2

					
				 
			return 0
		else:
			return 1
		
		
# The seer is supposed to be able to learn about the role of one player each night
class Seer:
	nightrole = 1
	order = 2
	@staticmethod
	def reveal(headers, game, connection):
		target = game.getplayerbyname(headers.target)
		# Check if the player is actually a seer, if the role currently woken up is seer, and if the target is alive
		if game.up == Seer and headers.sender.role == Seer and target.alive and headers.sender.alive:
			# Create packet
			packet = packets.SeerReveal(target.role.__name__, target.name)
			# Send packet containing the desired info to the seer
			game.send_packet(utils.obj_to_json(packet), connection)
			return 2
		return 1
		
# The hunter gets to kill a player of his choice upon death
class Hunter:
	nightrole = 0
	@staticmethod
	def kill(headers, game, connection):
		target = game.getplayerbyname(headers.target)
		if game.up == Hunter and headers.sender.role == Hunter and target.alive:
			game.kill_player(target, reason="hunter_kill")
			return 2
		return 1

# can prevent one person of his choosing from dying at each night	
class Protector(Role):
	nightrole = 1
	order = 1
	def __init__(self):
		super(Protector, self).__init__()
	
	@staticmethod
	def protect(headers, game, connection):
		target = game.getplayerbyname(headers.target)
    
		# if both protector and target are alive, modify the headers
		if headers.sender.alive and target.alive and game.up == Protector:
			target.protected = True
			return 2
		return 1

# The witch can kill and revive one player per game who died during the night.
# She is supposed to wake up last as she can only revive people who died during each night she wakes up in
class Witch(Role):
	nightrole = 1
	order = 4
	@staticmethod
	def kill(headers, game, connection):
		target = game.getplayerbyname(headers.target)
		if game.up == Witch and headers.sender.role == Witch and not headers.sender.haskilled and target.alive:
			game.kill_player(target)
			headers.sender.haskilled = 1
			return 2
		else:
			return 1
	@staticmethod
	def revive(headers, game, connection):
		target = game.getplayerbyname(headers.target)
		if game.up == Witch and headers.sender.role == Witch and not headers.sender.hasrevived and target in game.nightdeaths:
			# The witch can only save people who died during the night she wakes up, therefore removing them
			# from the nightdeaths list is what we want
			game.nightdeaths.remove(target)
			headers.sender.hasrevived = 1
			return 2
		else:
			return 1
	@staticmethod
	def onwakeup(game):
		dead = [i.name for i in game.nightdeaths]
		event = utils.obj_to_json(packets.Witch_send_dead(dead))
		game.sendrole(event, Witch)

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
