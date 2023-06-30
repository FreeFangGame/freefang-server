import struct

try:
	import freefang.utils as utils
	import freefang.packets as packets
	
except ImportError:
	import packets
	import utils


def readlength(con): # Read the length of the packet prepended to it

	try:
		unpack = con.recv(4) 
		leng = struct.unpack("<I", unpack)[0]
		return leng
	except:
		return None
			
def read_packet(con):
	length = readlength(con)
	if not length:
		return None
	return con.recv(length).decode()

def send_packet(packet, con):
	
	con.sendall(struct.pack("<I", len(packet)) + packet.encode()) 
		
# This function sends a success packet over a connection, this is just a cleaner way of doing it so you dont have to
# copy that long line all over the codebase
def send_success(con):
	send_packet(utils.obj_to_json(packets.Action_success()), con)
	
def send_failure(con, error):
	send_packet(utils.obj_to_json(packets.Action_failure(error=error)), con)

def send_message(sender, message, con):
    timestamp = utils.get_current_timestamp()
    chat_message = packets.ChatMessage(sender, message, timestamp)
    send_packet(utils.obj_to_json(chat_message), con)
    
