# FreeFang
 A free implementation of the Werewolf game in python.
 Currently in beta, however it is usable and all core features are implemented.

# Features

- Full werewolf experience with quite a few roles to pick from.  
- No moderator needed, the server takes care of everything from role attribution to voting to role actions.  
- Create a custom ruleset on game creation with only the roles you want.  
- No signup, enter a server, game id, pick a name and you're good.  
- Selfhostable, git clone, run freefang/main.py, done. No dependencies. Very simple to get started with.


# Clients

[freefang-qt](https://github.com/FreeFangGame/freefang-qt) is the reference client written by the devs.
You are free to write your own and PR to have it added here, full protocol documentation is coming.



# Protocol documentation
FreeFang clients and server communicate using TCP, packets are sent in the form of json prefixed by the packet length as 4 little endian bytes.  
In python this is done with `struct.pack("<I", length)`.  
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
Once a packet is sent, the server can reply with a packet with the action "action_success", "action_failure" or/and and another action related to the packet you've sent (i.e send you the role of a player if you revealed it as the seer).



