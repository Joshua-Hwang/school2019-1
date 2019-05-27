#!/bin/bash

python3 assign3.py 192.168.1.1/24 1024 << STDIN
gw get
gw set 192.168.1.30
gw get
msg 192.168.1.2 "hello"
arp get 192.168.1.2
arp set 192.168.1.2 2222
arp get 192.168.2
msg 192.168.1.2 "hello"
mtu get
mtu set 1600
mtu get
exit
STDIN
