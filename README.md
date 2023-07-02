# FreeFang
 A free implementation of [Werewolf](https://en.m.wikipedia.org/wiki/Mafia_(party_game)) (also known as Mafia) in python.
 Currently in beta, however it is usable and all core features are implemented.

# Gameplay
This game opposes two sides, the werewolves (minority) and the town (majority).
The goal of the town is to exterminate the werewolves and the goal of the werewolves is to reach numerical parity with the town.
The game happens in a cycle of night and day. During the night roles with different powers (such as finding out the role of another player) wake up and the werewolves vote to kill one non-werewolf.
During the day the town (with the werewolves hidden among them) vote to kill one player which they suspect to be a werewolf. The town does not know who the werewolves are and rely on clues/info given to them by the different roles.

This game is about social deduction, lying, persuasion, finding and using clues, etc.

# Getting started
The FreeFang server is available on pypi as `freefang-server`.  
To get started with hosting simply run  

`python -m pip install freefang-server`  
`freefang-server`  

For all the options available run `freefang-server -h`
# Features

- Full werewolf experience with quite a few roles to pick from.  
- No moderator needed, the server takes care of everything from role attribution to voting to role actions.  
- Create a custom ruleset on game creation with only the roles you want and more custom options!.  
- No signup, enter a server, game id, pick a name and you're good.  
- Selfhostable, very simple to get started with.


# Clients

[freefang-qt](https://github.com/FreeFangGame/freefang-qt) is the reference client written by the devs.
You are free to write your own and PR to have it added here, full protocol documentation is coming.


# Protocol documentation

Full protocol documentation in PROTOCOL.md with examples and complete descriptions.   


