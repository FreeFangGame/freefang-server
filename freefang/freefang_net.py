import struct

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
		
