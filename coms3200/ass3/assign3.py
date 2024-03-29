#!/usr/bin/env python3
import _thread
import sys
import socket

# the ARPTable is implemented with a dictionary
# the key is the IP and the value is the port
class ARPTable:
    def __init__(self, subnet, gateway=None):
        self._table = {}
        # gateway is gateway IP
        self.gateway = gateway
        self._subnet = subnet
    def __delitem__(self, key):
        self._table.__delitem__(key)
    def __getitem__(self, key):
        # if in subnet look for ARP entry return None if no port found
        # return None for missing gateway too
        # check if bits match up to the subnet*8th bit
        if self.in_subnet(key):
            # in subnet so look for it
            return self._table.get(key, None)
        else:
            # return gateway if available
            return self._table.get(self.gateway, None)
    def __setitem__(self, key, value):
        # ensure the key is in the subnet (all externals should be sent through
        # gateway)
        if len(self._table) == 0 or self.in_subnet(key):
            self._table.__setitem__(key, value)

    def get(self, key, default):
        return self._table.get(key, default)
    def in_subnet(self, key):
        left = bin_ip(key)[:self._subnet]
        right = bin_ip(next(iter(self._table.keys())))[:self._subnet]
        return bin_ip(key)[:self._subnet] == bin_ip(next(iter(self._table.keys())))[:self._subnet]

# contains the programs current IP, port, buffer size etc.
class ConnectionInfo:
    def __init__(self, fakeAddr, port):
        # initialise with server-side listening
        self.family = socket.AF_INET
        self.type = socket.SOCK_DGRAM
        self.ip = "localhost"
        self.fakeAddr = fakeAddr
        self.port = port # the port is the ll-addr
        self.mtu = 1500 # Maximum Transmission Unit (may change, default 1500)
        self.id = 1
    def create_sock(self):
        if hasattr(self, "_sock"):
            return
        self._sock = socket.socket(self.family, self.type)
        self._sock.bind((self.ip, self.port))
    def get_sock(self):
        return self._sock if hasattr(self, "_sock") else None
    @property
    def contentSize(self):
        # the spec says IHL is 5 always (20 bytes)
        return self.mtu - 20

# each fragment you put in the Fragment Holder should be of (offset, data)
# FragmentHolder also notes if the final packet is present or not
# NOTE: identifier isn't enough for uniqueness. Include source IP and ll-addr
# key = (IP, ll-addr, identifier)
class FragmentHolder:
    def __init__(self):
        self._datagrams = {}

    def set(self, srcIP, llAddr, identifier, offset, data, finished=False):
        key = (srcIP, llAddr, identifier)
        if key in self._datagrams:
            self.delete(*key)
        self.append(*key, offset, data, finished)

    def append(self, srcIP, llAddr, identifier, offset, data, finished=False):
        key = (srcIP, llAddr, identifier)
        # if doesn't exist, create
        if key not in self._datagrams:
            self._datagrams[key] = [finished, [(offset, data)]]
        else:
            # the final fragment is present or this is the final fragment
            self._datagrams[key][0] = self._datagrams[key][0] or finished
            self._datagrams[key][1] += [(offset, data)]

    def delete(self, srcIP, llAddr, identifier):
        key = (srcIP, llAddr, identifier)
        del self._datagrams[key]

    # you may need to tell the FragmentHolder this key is finished
    def force_finished(self, srcIP, llAddr, identifier, finished=True):
        key = (srcIP, llAddr, identifier)
        self._datagrams[key][0] = finished

    def is_finished(self, srcIP, llAddr, identifier):
        key = (srcIP, llAddr, identifier)
        return self._datagrams[key][0]

    # doesn't check for completeness but rather if there are gaps
    def has_gaps(self, srcIP, llAddr, identifier):
        key = (srcIP, llAddr, identifier)
        if key not in self._datagrams:
            return True
        currLength = 0
        packets = sorted(self._datagrams[key][1])
        # store sorted because that work should be saved
        self._datagrams[key][1] = packets
        for offset, data in packets:
            # ensure current length is equal to current packets offset
            if currLength != offset:
                return True
            currLength += len(data)
        return False

    def is_complete(self, srcIP, llAddr, identifier):
        key = (srcIP, llAddr, identifier)
        return self.is_finished(*key) and not self.has_gaps(*key)

    # call to convert the stored fragments of key into a single datagram
    # doesn't care if complete or not
    def defrag(self, srcIP, llAddr, identifier):
        key = (srcIP, llAddr, identifier)
        if key not in self._datagrams:
            return None
        ret = b""
        packets = sorted(self._datagrams[key][1])
        # store sorted because that work should be saved
        self._datagrams[key][1] = packets
        for _, data in packets:
            ret += data
        return ret

# converts an IP into its binary format (string of 1s and 0s)
def bin_ip(data):
    ret = ""
    parts = data.split('.')
    for part in parts:
        ret += bin(int(part))[2:].zfill(8)
    return ret

# parses 010101000 into an IP
def parse_ip(data):
    # each part of an IP is a byte
    ret = str(int(data[0:8], 2))
    # hardcoded because IPv4 addresses MUST be 32 bits
    for i in range(8,32,8):
        ret += '.'
        ret += str(int(data[i:i+8], 2))
    return ret

# converts the data into a dictionary
# we're assuming all packets are valid (not sure if this holds for the final
# 15 marks but oh well.
def read_packet(data):
    # the dictionary we will be returning
    ret = {}
    header = data[:20]
    content = data[20:]

    # convert our header into bits because it's easier
    headerBits = ''
    for c in header:
        # bin puts '0b' at the front
        # we also pad the left with 0s
        # NOTE: we can only do this assuming data is a byte string
        bits = bin(c)[2:].zfill(8)
        headerBits += bits

    ret['Version'] = int(headerBits[0:4], 2)
    ret['IHL'] = int(headerBits[4:8], 2)
    ret['DSCP'] = int(headerBits[8:14], 2)
    ret['ECN'] = int(headerBits[14:16], 2)
    ret['Total Length'] = int(headerBits[16:32], 2)
    ret['Identification'] = int(headerBits[32:48], 2)
    ret['Reserved flag'] = int(headerBits[48], 2) # should always be 0
    ret['DF flag'] = int(headerBits[49], 2)
    ret['MF flag'] = int(headerBits[50], 2)
    ret['Fragment Offset'] = int(headerBits[51:64], 2)
    ret['TTL'] = int(headerBits[64:72], 2)
    ret['Protocol'] = int(headerBits[72:80], 2)
    ret['Header Checksum'] = int(headerBits[80:96], 2)
    ret['Source IP'] = parse_ip(headerBits[96:128])
    ret['Destination IP'] = parse_ip(headerBits[128:160])
    ret['Content'] = content

    return ret

# the header should be equivalent to what is produced by read_packet
# header['Content'] is used for data if data is None
def print_packet(header, data=None):
    ipAddr = header['Source IP']
    # check protocol
    if header['Protocol'] == 0:
        data = header['Content'] if data is None else data
        print('\rMessage received from %s: "%s"\n> ' \
            % (ipAddr, data.decode()), end='')
    else:
        protocol = hex(header['Protocol'])
        print('\rMessage received from %s with protocol %s\n> ' \
            % (ipAddr, protocol), end='')
    sys.stdout.flush()

# when listening for a thread we need to remove the initial prompt then place
# our received messages then put our prompt back
# this is okay since no input gets through WHILE we're receiving.
def listen_loop(connInfo, arpTable):
    sock = connInfo.get_sock()

    # we store fragmented packets by their identifier until fully complete
    storedFragments = FragmentHolder()
    while True:
        data, addr = None, None
        try:
            # addr returns a tuple with (address, port)
            data, addr = sock.recvfrom(connInfo.mtu)
        except Exception as e:
            print(e)
            return

        llAddr = addr[1]
        # read IPv4 header
        packet = read_packet(data)
        # create tuple (src IP, ll-addr, id)
        key = (packet['Source IP'], llAddr, packet['Identification'])
        value = (packet['Fragment Offset'], packet['Content'])
        # is it a fragmented packet?
        # if printFrag is true we print that we got the whole thing
        printData = None
        if not packet['MF flag'] and not packet['Fragment Offset']:
            # complete packet
            # you don't have to printFrag since this is simple
            printData = packet['Content']
        else:
            if packet['MF flag']:
                # fragment found
                storedFragments.append(*key, *value)
            else:
                # last fragment
                storedFragments.append(*key, *value, finished=True)

            printData = storedFragments.defrag(*key) \
                if storedFragments.is_complete(*key) else None

        if printData is not None:
            print_packet(packet, printData)
        # they didn't say we need to add addr to our ARP

# create an IPv4 header for a single packet
# return it
# NOTE: ensure the DF flag is 0
# TTL should be seconds (localhost should be ~1 second and external ~30 idk)
# returns byte string
def construct_header(connInfo, destIP, totalLength, offset=0, mf=False):
    headerBits = ""
    headerBits += bin(4)[2:].zfill(4) # Version
    headerBits += bin(5)[2:].zfill(4) # IHL
    headerBits += bin(0)[2:].zfill(6) # DSCP - can be junk
    headerBits += bin(0)[2:].zfill(2) # ECN - can be junk
    headerBits += bin(totalLength)[2:].zfill(16) # Total Length
    headerBits += bin(connInfo.id)[2:].zfill(16) # Identification
    headerBits += bin(0)[2:].zfill(1) # Reserved flag - should always be 0
    headerBits += bin(0)[2:].zfill(1) # DF flag
    headerBits += bin(mf)[2:].zfill(1) # MF flag
    headerBits += bin(offset)[2:].zfill(13) # Fragment Offset
    headerBits += bin(30)[2:].zfill(8) # TTL
    headerBits += bin(0)[2:].zfill(8) # Protocol
    headerBits += bin(69)[2:].zfill(16) # Header Checksum - can be junk
    headerBits += bin_ip(connInfo.fakeAddr) # Source IP
    headerBits += bin_ip(destIP) # Destination IP

    header = b''
    for i in range(0,len(headerBits),8):
        header += chr(int(headerBits[i:i+8],2)).encode()
    return header

def send_packets(connInfo, llAddr, packets):
    sock = socket.socket(connInfo.family, connInfo.type)
    for packet in packets:
        sock.sendto(packet, (connInfo.ip, llAddr))

# returns a list of data all of appropriate size also considering headers
def split_data(connInfo, data):
    return [data[i:i+connInfo.contentSize] for i in range(0, len(data), connInfo.contentSize)]

# set the gateway IP address of the LAN the client is a part of to ipAddr
def gw_set(connInfo, arpTable, ipAddr):
    arpTable.gateway = ipAddr
# print the currently stored gateway IP address to stdout, or None
def gw_get(connInfo, arpTable):
    print(arpTable.gateway)
    sys.stdout.flush()
# insert a mapping from ipAddr to llAddr
def arp_set(connInfo, arpTable, ipAddr, llAddr):
    arpTable[ipAddr] = int(llAddr)
# print the currently stored link layer address mapped to ipAddr or None
def arp_get(connInfo, arpTable, ipAddr):
    print(arpTable[ipAddr])
    sys.stdout.flush()
# send a message
# ID should be incremented
def msg(connInfo, arpTable, ipAddr, payload):
    # check ipAddr is in ARP table
    llAddr = arpTable[ipAddr]
    if llAddr is not None:
        # check if payload < max content
        if len(payload) < connInfo.contentSize:
            # create a single packet
            # construct header
            header = construct_header(connInfo, ipAddr, len(payload))
            packet = header + payload.encode()
            send_packets(connInfo, llAddr, [packet])
        else:
            payloads = split_data(connInfo, payload)
            offset = 0
            packets = []
            for payload in payloads[:-1]:
                header = construct_header(connInfo, ipAddr, len(payload), offset, mf=True)
                packet = header + payload.encode()
                packets.append(packet)
                offset += len(payload)
            # final packet
            payload = payloads[-1]
            header = construct_header(connInfo, ipAddr, len(payload), offset, mf=False)
            packet = header + payload.encode()
            packets.append(packet)
            send_packets(connInfo, llAddr, packets)

        connInfo.id += 1
    else:
        # check if we're missing gateway or local
        if arpTable.in_subnet(ipAddr):
            print("No ARP entry found")
        else:
            print("No gateway found")
        sys.stdout.flush()
# set the MTU of the network's links as the specifed value
def mtu_set(connInfo, arpTable, value):
    connInfo.mtu = int(value)
# print the currently stored MTU
def mtu_get(connInfo, arpTable):
    print(connInfo.mtu)
    sys.stdout.flush()

# do the actions of the user
def input_loop(connInfo, arpTable):
    while True:
        cmd = input("> ")
        cmdParts = cmd.split(' ')
        if cmdParts[0] == "gw":
            if cmdParts[1] == "set":
                gw_set(connInfo, arpTable, cmdParts[2])
            elif cmdParts[1] == "get":
                gw_get(connInfo, arpTable)
        elif cmdParts[0] == "arp":
            if cmdParts[1] == "set":
                arp_set(connInfo, arpTable, cmdParts[2], cmdParts[3])
            elif cmdParts[1] == "get":
                arp_get(connInfo, arpTable, cmdParts[2])
        elif cmdParts[0] == "msg":
            payload = cmd.split('"')[1]
            msg(connInfo, arpTable, cmdParts[1], payload)
        elif cmdParts[0] == "mtu":
            if cmdParts[1] == "set":
                mtu_set(connInfo, arpTable, cmdParts[2])
            elif cmdParts[1] == "get":
                mtu_get(connInfo, arpTable)
        elif cmdParts[0] == "exit":
            break

# create a thread for listening and sending
def main(connInfo, arpTable):
    _thread.start_new_thread(listen_loop, (connInfo, arpTable))
    input_loop(connInfo, arpTable)

if __name__ == '__main__':
    # invocation must have argv[1] == ip-addr, argv[2] == ll-addr
    ipAddr, subnet = sys.argv[1].split('/')
    subnet = int(subnet)
    llAddr = int(sys.argv[2])
    connInfo = ConnectionInfo(ipAddr, llAddr)
    connInfo.create_sock()
    arpTable = ARPTable(subnet)
    # add your own ip and ll-addr for testing
    arpTable[ipAddr] = llAddr
    main(connInfo, arpTable)
