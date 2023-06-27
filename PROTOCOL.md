# Full protocol documentation

FreeFang clients and server communicate using TCP, packets are sent in the form of json prefixed by the packet length as 4 little endian bytes.
In python this is done with struct.pack("<I", length).
Each packet should have an action key that defines what it does and headers for extra info such as the target.
Other players are refered to by their usernames, which they choose upon game entry.
Example:

```json
{
  "action": "werewolf_vote",
  "headers": {
    "target": "Alice"
  }
}
```
```json
{
  "action": "cupid_infatuate",
  "headers": {
    "target1": "Alice",
    "target2": "Bob"
  }
}
```

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
gameid representts the ID of the game you want to join
Example:

```json
{
  "action": "game_join",
  "headers": {
    "name": "HectorSalamanca",
    "gameid": "game_id_here"
  }
}
```

### town_vote
This packet is sent upon voting during the day.
A player can only vote once, and can not vote for a dead player.
target represents the username of the player you're voting to kill.
Example:

```json
{
  "action": "town_vote",
  "headers": {
    "target": "KimWexler"
  }
}
```

### werewolf_vote
Same as town vote, but as a werewolf when werewolves get up.

```json
{
  "action": "werewolf_vote",
  "headers": {
    "target": "JessePinkman"
  }
}
```

### town_message
Send a message to town chat, only during the day

```json
{
  "action": "town_message",
  "headers": {
    "message": "Ignacio is sus guys"
  }
}
```

### werewolf_message
Same as town_message but when werewolves are up, this one is only forwarded to fellow werewolves by the server.

```json
{
  "action": "werewolf_message",
  "headers": {
    "message": "Hank is seer trust me guys 100%"
  }
}
```

### seer_reveal
Sent by the seer once he is woken up to obtain the role of one player.

```json
{
  "action": "seer_reveal"
  "headers": {
    "target": "Waltuh"
  }
}
```

### hunter_kill
Sent by the hunter once he is killed, he is allowed to kill anyone in the game.

```json
{
  "action": "hunter_kill",
  "headers": {
    "target": "Ehrmantraut"
  }
}
```

### protector_protect
Sent by the protector on wake up to protect a player for the night

Sent by the hunter once he is killed, he is allowed to kill anyone in the game.

```json
{
  "action": "protector_protect",
  "headers": {
    "target": "Hank"
  }
}
```






