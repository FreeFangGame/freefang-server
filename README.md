# FreeFang
 A free implementation of the Werewolf game in python.


# Protocol documentation
FreeFang clients and server communicate using TCP, packets are sent in the form of json prefixed by the packet length as 4 little endian bytes.  
In python this is done with `struct.pack("<I", length)`.  
Each packet should have an action key that defines what it does and headers for extra info such as the target.  
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
