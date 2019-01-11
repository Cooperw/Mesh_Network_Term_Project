
#!/usr/bin/env python3

import sys

from JCL_RF import RFDevicee

txdevice = None
txdevice = RFDevice(17)
txdevice.enable_tx()
txdevice.tx_code(str(sys.argv[1]), None, None)
txdevice.cleanup()
