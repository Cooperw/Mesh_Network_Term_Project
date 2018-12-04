#!/usr/bin/env python3

##########################################################################################################
#                           S  A  M  P  L  E     J  C  L    P  A  C  K  E  T                             #
##########################################################################################################
# Leading | Sender | Receiver | DateTime | Control Code | Part Num | Total Parts |   Data    | Check Sum #
#---------|--------|----------|----------|--------------|----------|-------------|-----------|-----------#
#    1    |   3    |     3    |    12    |       4      |     4    |      4      |    32     |     4     #
##########################################################################################################

import hashlib
import subprocess
import datetime
import re
import sys
import mmap

from JCL_RF import RFDevice

######################################################
# Vars

sender_len = 3;
receiver_len = 3;
datetime_len = 12;
control_code_len = 4;
part_num_len = 4;
total_parts_len = 4;
data_len = 32;
check_sum_len = 4;

######################################################
# Methods

def toBin(inp, length):
	partial = str(bin(int(inp)))[2:]
	return ('0' * (length-len(partial))) + partial

def maxBin(len):
	return 2**len-1

def extend(inp, length):
	return ('0' * (length-len(inp))) + inp

######################################################

# Set From Address, binary 1-7
from_adr = "010"

if(len(sys.argv) != 4):
	print(sys.argv[0] + " <to> <control_code> <message>")
	exit(1)

# Get To Address
#to_adr = input('To Address: ')
to_adr = sys.argv[1]
if(int(to_adr) > maxBin(sender_len) or int(to_adr) < 0):
	print("Addresses must be between 0 and "+str(maxBin(sender_len))+".")
	exit(1)
to_adr = toBin(to_adr, sender_len)

#Get Control Code
#control_code = input('Control Code: ')
control_code = sys.argv[2]
if(int(control_code) > maxBin(control_code_len) or int(control_code) < 0):
	print("Control codes must be between 0 and "+str(maxBin(control_code_len))+".")
	exit(1)
control_code = toBin(control_code, control_code_len)

#Build DTS
seconds = str(datetime.datetime.now(datetime.timezone.utc).timetuple().tm_hour * 3600 + datetime.datetime.today().timetuple().tm_min * 60 + datetime.datetime.today().timetuple().tm_sec)
seconds = str(int(seconds) % 3600)
seconds = toBin(seconds, datetime_len)

# Body
#message = input('Enter Message: ')
message = sys.argv[3]
j = int(data_len / 7)		#max ascii in a packet
n = j * maxBin(total_parts_len) #max ascii in a message
body = ''.join(format(ord(x), 'b').zfill(7) for x in message)
splitBody = [body[i:i+data_len] for i in range(0, len(body), data_len)]
part_total = len(splitBody)-1
if(part_total > maxBin(total_parts_len)):
	print("Messages can only be "+str(n)+" characters or less.");
	exit(1)
part_num = 0

myPackets = []

#Loop through pieces
for piece in splitBody:
	checksum = '00000000'

	#Header
	header  = to_adr
	header += from_adr
	header += seconds
	header += control_code

	part_num_bin = toBin(str(part_num), part_num_len)
	header += part_num_bin

	total_parts_bin = toBin(str(part_total), total_parts_len)
	header += total_parts_bin

	# Tack body to packet
	packet = header + piece

	# Tack checksum packet
	hash = hashlib.md5(packet.encode('utf-8')).hexdigest()
	checksum = bin(int(hash[-1], 16))[2:].zfill(4)
	packet += checksum

	#Output
	myPackets.append(packet)

	#Incriment for next packet
	part_num += 1

ackPackets = []
sendCount = 0
subprocess.Popen("echo '' > ack.log", shell=True, stdout=subprocess.PIPE)
with open("ack.log", "r+b") as file:
	while len(myPackets) is not len(ackPackets) and sendCount < 5:
		sendCount += 1
		print("Received "+str(len(ackPackets))+"/"+str(len(myPackets))+": "+str(ackPackets))
		for i in range(0,len(myPackets)):
			if i not in ackPackets:
				print(str(i)+":"+myPackets[i]) #binary packet

				#Set up Tx on GPIO 17
				rfdevice = RFDevice(17)
				rfdevice.enable_tx()
				rfdevice.tx_code(str(myPackets[i]))
				rfdevice.cleanup()

				try:
					mm = mmap.mmap(file.fileno(), 0)
					line = mm.readline().decode()
					ind = int(line[22:26], 2)
					mm.close()
					if ind not in ackPackets:
						ackPackets.append(ind)
				except:
					pass
