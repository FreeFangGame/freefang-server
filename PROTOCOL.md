# Full protocol documentation

FreeFang clients and server communicate using TCP, packets are sent in the form of json prefixed by the packet length as 4 little endian bytes.
In python this is done with struct.pack("<I", length).
Each packet should have an action key that defines what it does and headers for extra info such as the target.
Other players are refered to by their usernames, which they choose upon game entry.
Example:

{
  "action": "werewolf_vote",
  "headers": {
    "target": "Alice"
  }
}

{
  "action": "cupid_infatuate",
  "headers": {
    "target1": "Alice",
    "target2": "Bob"
  }
}

# Packet list
## Client
Those packets are sent by the client to interface with the server and play the game.

### game_create
This packet should be sent in order to create a game.  
playercap represents the number of players in the game while ruleset is a dictionnary containning each role in the game and how many people should have them.
Example:

```json
{
  "action": "game_create",
  "headers": {
    "playercap": 10,
    "ruleset": {
          "Werewolf": 3,
          "Villager": 5,
          "Seer": 1,
          "Hunter": 1
    }
  }
}
```

### game_join
This packet is sent upon joining a game.
name represents the username you choose to play as.
gameid representts the ID of the gams you want to join


