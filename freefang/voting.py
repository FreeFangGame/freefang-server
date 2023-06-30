"""
This file contains the code for the different voting schemes one can choose for each side
The schemes are absolute majority, relative majority, and unanimity.
"""

def unanimity(game):
	unanimity = all(i.target == game.votes[0].target for i in game.votes) 
	if not unanimity: # Check if everyone voted unanimously
		# No kill if unanimity is not achieved
		return 1
	else:
		# Kill the player that was unanimously voted
		kill = game.votes[0].target
		game.kill_player(kill)
		# Reset game.votes
		game.votes = []
		for i in game.players:
			i.voted = False # Set all players like they havent voted yet
		return 0

def relmaj(game):
	votes = {}
				
	# Gather all votes in a dictionary along with their target
	for i in game.votes:
		votes.setdefault(i.target, 0)
		votes[i.target] += 1
				
	# Get the highest number of votes on a player
	maxvotes = max(votes.values())
				
	# Check if that player is tied with another for the amount of votes he was targeted by
	ties = [key for key, value in votes.items() if value == maxvotes]
		

	for i in game.players:
		i.voted = False # Set all players like they havent voted yet
	game.votes = []
		
	# If there is a tie, no death (this is temporary, there may be vote altering roles in the future)
	if len(ties) > 1:
		return 1
				
	game.kill_player(ties[0])

def absmaj(game):
	votes = {}
	
	for i in game.votes:
		votes.setdefault(i.target, 0)
		votes[i.target] += 1
	
	for player, votes in votes.items():
		if votes > (len(game.alive)/2):
			game.kill_player(player)
			for i in game.players:
				i.voted = False # Set all players like they havent voted yet
			game.votes = []
				
			return 0
	for i in game.players:
		i.voted = False # Set all players like they havent voted yet
		game.votes = []
				
	return 1
			
		
		
