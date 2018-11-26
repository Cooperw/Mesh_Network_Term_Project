#!/usr/bin/env python3


################################################################################################
#           S  A  M  P  L  E      1  0  0    B  I  T      J  C      P  A  C  K  E  T           #
################################################################################################
# Sender | Receiver | DateTime | Control Code | Part Num | Total Parts |   Data    | Check Sum #
#--------|----------|----------|--------------|----------|-------------|-----------|-----------#
#   3    |     3    |    12    |       4      |     4    |      4      |    62     |     8     #
################################################################################################

import fileinput
import datetime
import binascii
import subprocess
import re
import sys

######################################################
# Vars

sender_len = 3
receiver_len = 3
datetime_len = 12
control_code_len = 4
part_num_len = 4
total_parts_len = 4
data_len = 62
check_sum_len = 8
header_len = sender_len + receiver_len + datetime_len + control_code_len;
c = 0 #packet cursor

######################################################
# Methods

def extract(str, len):
	global c
	part = str[c:c+len]
	c += len
	return part

def bitstring_to_bytes(s):
    return int(s, 2).to_bytes(len(s) // 7, byteorder='big')

def verfiy_packets(packets):
	count = 0
	for packet in packets:
		if int(packet[header_len:header_len+part_num_len], 2) == count:
			count += 1
		else:
			return False
	return True

######################################################

processed = []

lines = []
with open("/home/pi/370_Term_Project/unprocessed_packets.log","r") as input:
	for line in input:
		if(len(line) > header_len):
			lines.append(line)

headers = set([])
for line in lines:
	headers.add(line[:header_len])

for header in headers:
	packets = []
	for line in lines:
		if line[:header_len] == header:
			packets.append(line)

	packets.sort()

	if verfiy_packets(packets):

		message = ""
		for packet in packets:
			message += packet[header_len+part_num_len+total_parts_len:-9]
			processed.append(packet)
		c = 0

		entry = []

		entry.append(str(int(extract(packet, sender_len), 2)))
		entry.append(str(int(extract(packet, receiver_len), 2)))
		entry.append(int(extract(packet, datetime_len), 2)/60)
		entry.append(str(int(extract(packet, control_code_len), 2)))

		splitMessage = [message[i:i+7] for i in range(0, len(message), 7)]
		ascii = "";
		for character in splitMessage:
			ascii += bitstring_to_bytes(character).decode()
		entry.append(ascii)



		#Process message
		if(int(entry[3]) == 0):
			#ACK
			pass
		elif (int(entry[3]) == 1):
			#Text
			print("To:\t"+entry[0])
			print("From:\t"+entry[1])
			#print("Date:\t"+entry[2])
			print("Message:\t"+entry[4])

		elif (int(entry[3]) == 2):
			#Encrypted Text
			print("To:\t"+entry[0])
			print("From:\t"+entry[1])
			#print("Date:\t"+entry[2])
			print("Message:\t"+entry[4])

		elif (int(entry[3]) == 3):
			#RCE
			print("To:\t"+entry[0])
			print("From:\t"+entry[1])
			#print("Date:\t"+entry[2])
			print("Command: "+entry[4])

			subprocess.Popen(entry[4], shell=True)

		elif (int(entry[3]) == 4):
			#Encrypted RCE
			pass
		else:
			#Unknown
			print("Control Code Unknown!")
			print(entry)

with open("/home/pi/370_Term_Project/unprocessed_packets.log","r") as input:
	with open("/home/pi/370_Term_Project/unprocessed_packets.tmp","w") as output:
		for line in input:
			if line not in processed:
				if len(line) > header_len:
					output.write(line)
subprocess.call(['mv','/home/pi/370_Term_Project/unprocessed_packets.tmp','/home/pi/370_Term_Project/unprocessed_packets.log'])
