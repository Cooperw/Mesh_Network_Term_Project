#!/usr/bin/env python3


################################################################################################
#           S  A  M  P  L  E      1  0  0    B  I  T      J  C      P  A  C  K  E  T           #
################################################################################################
# Sender | Receiver | DateTime | Control Code | Part Num | Total Parts |   Data    | Check Sum #
#--------|----------|----------|--------------|----------|-------------|-----------|-----------#
#   3    |     3    |    12    |       4      |     4    |      4      |    62     |     8     #
################################################################################################

import subprocess
import datetime
import re
import sys

######################################################
# Vars

sender_len = 3;
receiver_len = 3;
datetime_len = 12;
control_code_len = 4;
part_num_len = 4;
total_parts_len = 4;
data_len = 62;
check_sum_len = 8;

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

# Set From Address
from_adr = "011"

# Get To Address
to_adr = input('To Address: ')
if(int(to_adr) > maxBin(sender_len) or int(to_adr) < 0):
	print("Addresses must be between 0 and "+str(maxBin(sender_len))+".")
	exit(1)
to_adr = toBin(to_adr, sender_len)

#Get Control Code
control_code = input('Control Code: ')
if(int(control_code) > maxBin(control_code_len) or int(control_code) < 0):
	print("Control codes must be between 0 and "+str(maxBin(control_code_len))+".")
	exit(1)
control_code = toBin(control_code, control_code_len)

#Build DTS
seconds = str(datetime.datetime.now(datetime.timezone.utc).timetuple().tm_hour * 3600 + datetime.datetime.today().timetuple().tm_min * 60 + datetime.datetime.today().timetuple().tm_sec)
seconds = str(int(seconds) % 3600)
seconds = toBin(seconds, datetime_len)

# Body
message = input('Enter Message: ')
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
	packet += checksum

	#Output
	myPackets.append(packet)

	#Incriment for next packet
	part_num += 1

for packet in myPackets:
	print(packet) #binary packet
	bashCommand = "python3 send.py " + str(packet)
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	output, error = process.communicate()
