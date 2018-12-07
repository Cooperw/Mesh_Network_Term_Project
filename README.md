# 370_Term_Project
 
 [Demo Video](https://www.youtube.com/watch?v=o8EDP-yPp6c)
 [Research Paper](https://drive.google.com/open?id=1yzBuh9Xlhe53lLmGqgGAuuPcmVzS0D-d)
 
 Developed by Cooper Wiegand, John Vanderhoofven, and Jiping Lu at Colorado State University.

## Overview ##
A set of programs that operate a rudementary mesh-type network. The network currently communicates over standard 433 MHz chips and can exchange text messages as well as commands which are run automatically on the destination device in a fork/exec model. The 433 MHz setup relies on JCL_RF.py and the origional "library" can be found at https://pypi.org/project/rpi-rf/.

#### Packet Structure ####
```
##########################################################################################################
#                           S  A  M  P  L  E     J  C  L    P  A  C  K  E  T                             #
##########################################################################################################
# Leading | Receiver | Sender | DateTime | Control Code | Part Num | Total Parts |   Data    | Check Sum #
#---------|----------|--------|----------|--------------|----------|-------------|-----------|-----------#
#    1    |   3      |   3    |    12    |       4      |     4    |      4      |    32     |     4     #
##########################################################################################################

Sender and receiver are 3 bit addresses.

Datetime is the number of seconds that have passed in the last hour.
We can only guarentee accuracy of packets that reach their destination within 1 hour.

The control code is a 4 bit number which determines how the data is processed:
0: ACK
1: Clear-text Text Message
2: Encrypted Text Message (Unimplimented)
3: Clear-text Remote Code Execution
4: Encrypted Remote Code Execution (Unimplimented)
5-15: Undefined

Part Num and Total Parts together allow for a message to be divided up to a maximum of 
16 parts which are re-assembled by the receiver.

You might have noticed the leading '1'. This is so that leading zeros are not lost during 
transmission. Our new library takes care of this bit automatially.
```

## Setup ##
- Add your device "phone number" to builder.py and receiver.py (should be a binary 1-7)

- Follow the wiring diagrams found at https://pypi.org/project/rpi-rf/#wiring-diagram-example.

- Start your receiver and you should now be part of the network

## Receiving ##

#### Start Listener ####
```
pi@handset1:~/370_Term_Project $ ./listener.py 
New data from 2!
Forwarding from 4 to 3!
New data from 2!
New data from 2!
```

#### View Texts ####
```
pi@handset1:~/370_Term_Project $ cat newMessages.log 
To:     0
From:   2
Date:   03:29:19 MST, 12/04/2018
Message:        Hey!
To:     1
From:   2
Date:   04:51:05 MST, 12/04/2018
Message:        Hello how are you?
```

## Sending ##

#### Send Example (Text) ####
We will be sending a message from device 2 to device 1. As you can see, 4 packets go out and when they
are received an acknowledgement is sent back so that we know our packet has arrived. Notice that packet 0 
needed to be sent 3 times but packets 1-3 made it on the first attempt. The builder will only send a packet
up to 5 times.
```
pi@handset2:~/370_Term_Project $ ./builder.py 
./builder.py <to> <control_code> <message>
pi@handset2:~/370_Term_Project $ ./builder.py 1 1 "Hello how are you?"
Received 0/4: []
0:001010110001010101000100000011100100011001011101100110110011010100
1:001010110001010101000100010011111010000011010001101111111011100001
2:001010110001010101000100100011100000110000111100101100101010001010
3:0010101100010101010001001100110011110011101111111010101111111011
Received 2/4: [1, 2]
0:001010110001010101000100000011100100011001011101100110110011010100
Received 3/4: [1, 2, 3]
0:001010110001010101000100000011100100011001011101100110110011010100
```

#### Send Example (broadcasting a command) ####
We sent a command to all devices on our network. The 0 below means broadcast and the 3 means this is executable
in a terminal and not a text message. Broadcasts do not supports acks like texts do but each packet is still
sent 5 times.
```
pi@handset2:~/370_Term_Project $ ./builder.py 0 3 "sudo activateLights"
Received 0/5: []
0:000010000011011110001100000100111001111101011100100110111101001000
1:000010000011011110001100010100000110000111000111110100110100110110
2:000010000011011110001100100100110110110000111101001100101100111001
3:000010000011011110001100110100001101001110011111010001110100111010
4:000010000011011110001101000100100110010
```
