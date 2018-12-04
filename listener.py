#!/usr/bin/env python3

##########################################################################################################
#                           S  A  M  P  L  E     J  C  L    P  A  C  K  E  T                             #
##########################################################################################################
# Leading | Sender | Receiver | DateTime | Control Code | Part Num | Total Parts |   Data    | Check Sum #
#---------|--------|----------|----------|--------------|----------|-------------|-----------|-----------#
#    1    |   3    |     3    |    12    |       4      |     4    |      4      |    32     |     4     #
##########################################################################################################

import hashlib
import argparse
import signal
import sys
import time
import logging
import subprocess
import mmap

from JCL_RF import RFDevice

######################################################
# Vars

sender_len = 3
receiver_len = 3
datetime_len = 12
control_code_len = 4
part_num_len = 4
total_parts_len = 4
data_len = 32
check_sum_len = 4
header_len = sender_len + receiver_len + datetime_len + control_code_len;

rxdevice = None
txdevice = None

#Binary number 1-7
number = "010"

def SendAck(inbound):
	packet = ""
	packet += inbound[3:6]	#recieve
	packet += inbound[:3]	#send
	packet += inbound[6:18]	#time
	packet += "0000"		#cc
	packet += inbound[22:30]		##parts

	hash = hashlib.md5(packet.encode('utf-8')).hexdigest()
	checksum = bin(int(hash[-1], 16))[2:].zfill(4)
	packet += checksum

	txdevice = RFDevice(17)
	txdevice.enable_tx()
	txdevice.tx_code(str(packet))
	txdevice.cleanup()

def ForMe(inbound, Ack):
	packet = inbound[:-4]
	hash = hashlib.md5(packet.encode('utf-8')).hexdigest()
	checksum = bin(int(hash[-1], 16))[2:].zfill(4)

	if(checksum == inbound[-4:]):
		if(inbound[18:22] == "0000"):
			#ACK
			print("New Ack!")
			with open("ack.log", "wb") as file:
				file.write(str.encode(inbound))
		else:
			print("New data from "+str(int(inbound[3:6], 2))+"!")
			bashCommand = "echo " + inbound + " >> unprocessed_packets.log"
			process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE, shell=True)
			output, error = process.communicate()
			if Ack:
				SendAck(inbound)
	else:
		print(inbound)

def Forward(inbound):
	packet = inbound[:-4]
	hash = hashlib.md5(packet.encode('utf-8')).hexdigest()
	checksum = bin(int(hash[-1], 16))[2:].zfill(4)

	if(checksum == inbound[-4:] and inbound[3:6] != "000" and inbound[3:6] != number):
		print("Forwarding from "+str(int(inbound[3:6], 2))+" to "+str(int(inbound[:3], 2))+"!")
		txdevice = RFDevice(17)
		txdevice.enable_tx()
		txdevice.tx_code(str(inbound))
		txdevice.cleanup()

def exithandler(signal, frame):
	rxdevice.cleanup()
	sys.exit(0)

###################################################33

signal.signal(signal.SIGINT, exithandler)
timestamp = None
past_packets = []

# Listen on GPIO 27
rxdevice = RFDevice(27)
rxdevice.enable_rx()

while True:
	if rxdevice.rx_code_timestamp != timestamp:
		timestamp = rxdevice.rx_code_timestamp
	if(len(str(rxdevice.rx_code)) > 20):
		inbound = str(rxdevice.rx_code)
		rxdevice.rx_code = 0;

		#Filters only duplicates within a session
		if inbound not in past_packets:
			past_packets.append(inbound)
			if inbound[:3] == "000":
				#Capture and relay broadcast
				ForMe(inbound, False)
				Forward(inbound)
			else:
				if inbound[:3] == number:
					#For me
					ForMe(inbound, True)
				else:
					#Not for me, forward
					Forward(inbound)
#		else Duplicate dropped
	time.sleep(0.01)
rxdevice.cleanup()
