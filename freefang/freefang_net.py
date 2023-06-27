import struct
import freefang.freefang_utils as utils
import freefang.packets as packets

def readlength(con): # Read the length of the packet prepended to it
	unpack = con.recv(4) 
	leng = 0
	try:
		leng = struct.unpack("<I", unpack)[0]
		return leng
	except:
		return None
			
def read_packet(con):
    length = readlength(con)
    if not length:
        return None
    packet = con.recv(length).decode()
    if not packet:
        return None
    action = utils.json_to_object(packet).action
    if action == "chat_message":
        handle_message(packet)
    return packet

def send_packet(packet, con):
	
	con.sendall(struct.pack("<I", len(packet)) + packet.encode()) 
		
# This function sends a success packet over a connection, this is just a cleaner way of doing it so you dont have to
# copy that long line all over the codebase
def send_success(con):
	send_packet(utils.obj_to_json(packets.Action_success()), con)
	
def send_failure(con, error):
	send_packet(utils.obj_to_json(packets.Action_failure(error=error)), con)

def send_message(con, sender, recipient, message):
    timestamp = utils.get_current_timestamp()
    chat_message = packets.ChatMessage(sender, recipient, message, timestamp)
    send_packet(utils.obj_to_json(chat_message), con)
    
def handle_message(packet):
    chat_message = utils.json_to_object(packet)
    sender = chat_message.headers.sender
    recipient = chat_message.headers.recipient
    message = chat_message.headers.message
    timestamp = chat_message.headers.timestamp
    # just temporary, display this on the recipient side
    print(f"[{timestamp}] {sender}: {message} to {recipient}")
