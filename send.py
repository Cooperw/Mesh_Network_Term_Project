
#!/usr/bin/env python3

import argparse
import logging

from JC_RF import RFDevice

parser = argparse.ArgumentParser(description='Sends a decimal code via a 433/315MHz GPIO device')
parser.add_argument('code', metavar='CODE', type=str,
                    help="Decimal code to send")
parser.add_argument('-g', dest='gpio', type=int, default=17,
                    help="GPIO pin (Default: 17)")
parser.add_argument('-p', dest='pulselength', type=int, default=None,
                    help="Pulselength (Default: 350)")
parser.add_argument('-t', dest='protocol', type=int, default=None,
                    help="Protocol (Default: 1)")
args = parser.parse_args()

rfdevice = RFDevice(args.gpio)
rfdevice.enable_tx()

if args.protocol:
    protocol = args.protocol
else:
    protocol = "default"
if args.pulselength:
    pulselength = args.pulselength
else:
    pulselength = "default"
logging.info(str(args.code) +
             " [protocol: " + str(protocol) +
             ", pulselength: " + str(pulselength) + "]")

rfdevice.tx_code(args.code, args.protocol, args.pulselength)
rfdevice.cleanup()
