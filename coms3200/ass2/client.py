#!/usr/bin/env python3
import socket
import sys
from scapy.packet import Packet
from scapy.fields import ByteField, ShortField, BitField
from scapy.all import *


LOCALHOST = "127.0.0.1"
FILE_NAME = "file.txt"

PACKET_SIZE = 1472
PAYLOAD_SIZE = 1466
PAYLOAD_SIZE_BITS = PAYLOAD_SIZE * 8

RECV_SIZE = 1500

SEND_MODE = "Sent packet to"
RECV_MODE = "Received packet from"


def str_to_int(string, pad=PAYLOAD_SIZE):
    b_str = string.encode("UTF-8")
    if pad is not None:
        for i in range(len(string), pad):
            b_str += b'\0'
    return int.from_bytes(b_str, byteorder='big')


def int_to_str(integer, size=PAYLOAD_SIZE):
    return integer.to_bytes(size, byteorder='big').rstrip(b'\x00').decode("UTF-8")


class RUSH(Packet):
    name = "RUSH"
    fields_desc = [
        ShortField("seq_num", 0),
        ShortField("ack_num", 0),
        BitField("ack_flag", 0, 1),
        BitField("nak_flag", 0, 1),
        BitField("get_flag", 0, 1),
        BitField("dat_flag", 0, 1),
        BitField("fin_flag", 0, 1),
        BitField("reserved", 0, 11),
        BitField("data", 0, PAYLOAD_SIZE_BITS)
    ]


"""
DEBUG Level 0 - Do not print anything
DEBUG Level 1 - Print packet headers
DEBUG Level 2 - Print packet headers + data
"""


class Connection:
    def __init__(self, my_ip, my_port, serv_ip, serv_port, debug_level=1):
        self._my_info = (my_ip, my_port)
        self._serv_info = (serv_ip, serv_port)
        self._socket = None
        self._seq_num = 1
        self._debug_level = debug_level

    def _print(self, pkt, port, mode):
        output = ""
        if self._debug_level > 0:
            output += "{} port {}:\n    (seq_num={}, ack_num={}, flags={}{}{}{}{})".format(mode, port, pkt.seq_num,
                        pkt.ack_num, pkt.ack_flag, pkt.nak_flag, pkt.get_flag, pkt.dat_flag, pkt.fin_flag)
        if self._debug_level == 2:
            output += "\n    Data: {}".format(repr(int_to_str(pkt.data)))
        print(output + "\n")

    def connect(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.bind(self._my_info)
            return True
        except socket.error as err:
            print("Error encountered when opening socket:\n", err)
            return False

    def close(self):
        self._socket.close()

    def send_request(self, resource):
        pkt = RUSH(seq_num=self._seq_num, get_flag=1, data=str_to_int(resource))
        self._socket.sendto(raw(pkt), self._serv_info)
        self._seq_num += 1
        self._print(pkt, self._serv_info[1], SEND_MODE)

    def recv_pkt(self):
        raw_data, info = self._socket.recvfrom(RECV_SIZE)
        assert len(raw_data) <= PACKET_SIZE, "Received overlong packet: " + repr(raw_data)
        try:
            return RUSH(raw_data), info
        except:
            assert False, "Could not decode packet: " + repr(raw_data)

    def run(self):
        while True:
            pkt, info = self.recv_pkt()
            self._print(pkt, info[1], RECV_MODE)
            if pkt.fin_flag == 1 and all(i == 0 for i in (pkt.ack_flag, pkt.nak_flag, pkt.dat_flag, pkt.get_flag)):
                cli_fin_ack = RUSH(seq_num=self._seq_num, ack_num=pkt.seq_num, fin_flag=1, ack_flag=1)
                self._socket.sendto(raw(cli_fin_ack), self._serv_info)
                self._seq_num += 1
                self._print(cli_fin_ack, self._serv_info[1], SEND_MODE)

                while True:
                    serv_fin_ack, info = self.recv_pkt()
                    self._print(serv_fin_ack, info[1], RECV_MODE)
                    if serv_fin_ack.fin_flag == 1 and serv_fin_ack.ack_flag == 1 and \
                            all(i == 0 for i in (serv_fin_ack.nak_flag, serv_fin_ack.dat_flag, serv_fin_ack.get_flag)):
                        return  # end of connection
            elif pkt.dat_flag == 1:
                ack = RUSH(seq_num=self._seq_num, ack_num=pkt.seq_num, dat_flag=1, ack_flag=1)
                self._socket.sendto(raw(ack), self._serv_info)
                self._seq_num += 1
                self._print(ack, self._serv_info[1], SEND_MODE)


def main(argv):
    if len(argv) <= 2 or not argv[1].isdigit() or not argv[2].isdigit():
        print("Usage: python3 client.py client_port server_port [verbosity]")
        return

    my_port = int(argv[1])
    serv_port = int(argv[2])

    debug_level = 1
    if len(argv) > 2:
        if argv[1] in ("0", "1", "2"):
            debug_level = int(argv[1])

    conn = Connection(LOCALHOST, my_port, LOCALHOST, serv_port, debug_level)
    if not conn.connect():
        return

    try:
        conn.send_request(FILE_NAME)
        conn.run()
    except AssertionError as e:
        print(e.args[0])

    conn.close()

if __name__ == "__main__":
    main(sys.argv)

