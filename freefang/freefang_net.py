import struct
import freefang_utils as utils
import packets

def readlength(con): # Read the length of the packet prepended to it
	unpack = con.recv(4) 
	return struct.unpack("<I", unpack)[0] #TODO: Handle packets without length header
			
def read_packet(con):
	length = readlength(con)
	if not length:
		return None
	packet = con.recv(length).decode()
	if not packet:
		return None
	return packet

def send_packet(packet, con):
	
	con.sendall(struct.pack("<I", len(packet)) + packet.encode()) 
		
# This function sends a success packet over a connection, this is just a cleaner way of doing it so you dont have to
# copy that long line all over the codebase
def send_success(con):
	send_packet(utils.obj_to_json(packets.Action_success()), con)
	
def send_failure(con, error):
	send_packet(utils.obj_to_json(packets.Action_failure(error=error)), con)
