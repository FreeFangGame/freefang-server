def readlength(con): # Read the length of the packet prepended to it
	buf = ""
	for i in range(12): 
		buff = con.recv(1).decode()
		if buff == "\r":
			return int(buf) # \r is the delimeter
		else:
			buf += buff
	return None # If length header is not stopped after 12 bytes we bail out 
			
def read_packet(con):
	length = readlength(con)
	if not length:
		return None
	packet = con.recv(length).decode()
	if not packet:
		return None
	return packet

def send_packet(packet, con):
	head = str(len(packet)) + "\r" # Prepend packet length to our message and add \r as delimeter
	con.sendall((head + packet).encode()) 
		
