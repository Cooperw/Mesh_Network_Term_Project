# 370_Term_Project

 Developed by Cooper Wiegand, John Vanderhoofven, and Jiping Lu at Colorado State University. 

## Overview ##
A set of programs that operate a rudementary mesh-type network. The network currently communicates over standard 433 MHz chips and can exchange text messages as well as commands which are run automatically on the destination device in a fork/exec model. The 433 MHz setup relies on JCL_RF.py and the origional "library" can be found at https://pypi.org/project/rpi-rf/.

#### Packet Structure ####
```
################################################################################################
#           S  A  M  P  L  E      1  0  0    B  I  T      J  C  L    P  A  C  K  E  T          #
################################################################################################
# Sender | Receiver | DateTime | Control Code | Part Num | Total Parts |   Data    | Check Sum #
#--------|----------|----------|--------------|----------|-------------|-----------|-----------#
#   3    |     3    |    12    |       4      |     4    |      4      |    62     |     8     #
################################################################################################

Sender and receiver are 3 bit addresses.

Datetime is the number of seconds that have passed in the last hour.
We can only guarentee accuracy of packets that reach their destination within 60 miniutes.

The control code is a 4 bit number which determines how the data is processed:
0: ACK
1: Clear-text Text Message
2: Encrypted Text Message
3: Clear-text Remote Code Execution
4: Encrypted Remote Code Execution
5-15: Undefined

Part Num and Total Parts together allow for a message to be divided up to a maximum of 
16 parts which are re-assembled by the receiver.
```

## Setup ##
- Add your device "phone number" to builder.py and receiver.py (should be a binary 1-7)

- Add crontab entry
```
* * * * * /home/pi/370_Term_Project/process_packets.py >> /home/pi/370_Term_Project/newMessages.log
```

- Follow the wiring diagrams found at https://pypi.org/project/rpi-rf/#wiring-diagram-example.

- Start your receiver and you should now be part of the network

## Receiving ##

#### Start Receiver ####
```
./receive.py
```

#### View Texts ####
```
cat ./newMessages.log
```

## Sending ##

#### Send Example (sending text to device 2) ####
```
./builder.py 
To Address: 2
Control Code: 1
Enter Message: Hello how are you doing today?
0100010110010111000001000000111001000110010111011001101100110111101000001101000110111111101100000000
0100010110010111000001000100111010000011000011110010110010101000001111001110111111101010100000000000
0100010110010111000001001000110011001001101111110100111011101100111010000011101001101111110000000000
01000101100101110000010011001110011000011111001011111100000000
```

#### Send Example (broadcasting a command) ####
```
./builder.py 
To Address: 0
Control Code: 3
Enter Message: date > ~/now
0000010111010010010011000000011100100110000111101001100101010000001111100100000111111001011100000000
000001011101001001001100010001111011101101111111011100000000
```
