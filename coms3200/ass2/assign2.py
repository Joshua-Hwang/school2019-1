#!/usr/bin/env python3
import sys
import socket

class ConnectionInfo:
    def __init__(self):
        # initialise with server-side listening
        self.family = socket.AF_INET
        self.type = socket.SOCK_DGRAM
        self.ip = "localhost"
        self.port = 43775 # ZZZ - should be 0 not declared yet
        self.buffer_size = 1500 # as declared in the spec

    def add_sock(self, sock):
        self._sock = sock
    def get_sock(self):
        return self._sock if hasattr(self, "_sock") else None
    # when you get a return address to send to
    def add_addr(self, addr):
        self._addr = addr
    def get_addr(self):
        return self._addr if hasattr(self, "_addr") else None

class RushPacket:
    ACK = 0b10000000
    NAK = 0b01000000
    GET = 0b00100000
    DAT = 0b00010000
    FIN = 0b00001000

    def __init__(self, seq_num, ack_num, flags, payload):
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.flags = flags
        self.payload = payload
    
    def get_flag(self, flag):
        return bool(self.flags & flag)

# creates a socket and returns it
def create_sock(conn_info):
    sock = socket.socket(conn_info.family, conn_info.type)
    sock.bind((conn_info.ip, conn_info.port))
    return sock

# attempts to read a rush header
# returns a RushPacket if successful and returns None for any failure
def parse_rush_packet(data):
    seq_num = int.from_bytes(data[:2], byteorder='big')
    ack_num = int.from_bytes(data[2:4], byteorder='big')
    flags = data[4]
    payload = data[6:].rstrip(b'\x00')
    # ensure seq_num isn't 0
    if seq_num == 0:
        return None
    # ensure flags make sense
    ret = RushPacket(seq_num, ack_num, flags, payload)
    bit_count = bin(ret.flags).count('1')
    if bit_count > 2 or bit_count == 0:
        return None

    if bit_count == 2:
        # DAT/ACK and FIN/ACK are the only double headers
        dat_ack_present = ret.get_flag(RushPacket.DAT) \
            and ret.get_flag(RushPacket.ACK)
        fin_ack_present = ret.get_flag(RushPacket.FIN) \
            and ret.get_flag(RushPacket.ACK)

        if not (dat_ack_present or fin_ack_present):
            return None

    return ret

# returns the header info or None
def parse_GET(data):
    # note: data doesn't come with ip or udp headers
    header = parse_rush_packet(data);
    # check for GET flag (AND  no other flags)
    # sequence number is guaranteed to be 1
    return header if header and header.get_flag(RushPacket.GET) \
        and (header.seq_num == 1) \
        else None

def send_content(conn_info, content):
    # split content into buffer sized pieces
    # wait for the ACK packet then send next DAT

def send_and_listen_packet(conn_info, payload):
    sock.sendto(payload, conn_info.get_addr())
    while True:
        data, addr = sock.recvfrom(conn_info.buffer_size)
        # ensure same client
        if addr != conn_info.get_addr():
            continue
        # check for ACK
        packet = parse_rush_packet(data)
        if not (packet.get_flag(RushPacket.ACK)
                and packet.get_flag(RushPacket.DAT)):
            # check for NAK
            if packet.get_flag(RushPacket.NAK):
                # ensure sequence number and ack number make sense
                # if so send sock.sendto again
            continue
        # ensure sequence number and ack number make sense
        break
        # If an NAK or 3 seconds pass resend

def main(conn_info):
    # create connection
    sock = create_sock(conn_info)
    # assuming we're using an ephemeral port let's just grab it from sock
    conn_info.add_sock = sock
    conn_info.port = sock.getsockname()[1]
    print(conn_info.port)
    # listen for GET requests
    get_packet = ""
    while True:
        # note: data doesn't come with ip or udp headers
        data, addr = sock.recvfrom(conn_info.buffer_size)
        if data:
            conn_info.add_addr(addr)
            get_packet = parse_GET(data)
            if get_packet:
                break;
    
    # get file
    content = b''
    with open(get_packet.payload.decode('utf-8'), 'rb') as content_file:
        content = content_file.read()
    # send data through DAT packets (stop and wait)
    send_content(conn_info, content)
    # send FIN once data is sent
    # If the packet doesn't make sense just ignore it
    # listen for FIN/ACK header
    # send your own FIN/ACK and close the connection

if __name__ == '__main__':
    conn_info = ConnectionInfo()
    main(conn_info);
