#!/usr/bin/env python3

import argparse
import signal
import sys
import time
import logging
import subprocess

from JC_RF import RFDevice

rfdevice = None
number = "011"

def ForMe(inbound):
	print("New data from "+str(int(inbound[3:6], 2))+"!")
	bashCommand = "echo " + inbound + " >> unprocessed_packets.log"
	process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE, shell=True)
	output, error = process.communicate()

def Forward(inbound):
	print("Forwarding from "+str(int(inbound[3:6], 2))+" to "+str(int(inbound[:3], 2))+"!")
	bashCommand = "python3 send.py " + str(inbound)
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	output, error = process.communicate()

# pylint: disable=unused-argument
def exithandler(signal, frame):
	rfdevice.cleanup()
	sys.exit(0)

parser = argparse.ArgumentParser(description='Receives a decimal code via a 433/315MHz GPIO device')
parser.add_argument('-g', dest='gpio', type=int, default=27,
			help="GPIO pin (Default: 27)")
args = parser.parse_args()

signal.signal(signal.SIGINT, exithandler)
rfdevice = RFDevice(args.gpio)
rfdevice.enable_rx()
timestamp = None
logging.info("Listening for codes on GPIO " + str(args.gpio))

past_packets = []
while True:
	if rfdevice.rx_code_timestamp != timestamp:
		timestamp = rfdevice.rx_code_timestamp
		logging.info(str(rfdevice.rx_code) +
                     " [pulselength " + str(rfdevice.rx_pulselength) +
                     ", protocol " + str(rfdevice.rx_proto) + "]")
	if(len(str(rfdevice.rx_code)) > 20):
		inbound = str(rfdevice.rx_code)
		rfdevice.rx_code = 0;

		#Filters only duplicates within a session
		if inbound not in past_packets:
			past_packets.append(inbound)
			if inbound[:3] == "000":
				#Capture and relay broadcast
				ForMe(inbound)
				Forward(inbound)
			else:
				if inbound[:3] == number:
					#For me
					ForMe(inbound)
				else:
					#Not for me, forward
					Forward(inbound)
#		else Duplicate dropped
	time.sleep(0.01)
rfdevice.cleanup()
