#!/usr/bin/python3.8
from .packets import Packets as Packets
import base64


class Ack:
    def __init__(self, hopAddress, prevHopAddress):
        self.hopAddr = hopAddress
        self.prevHopAddr = prevHopAddress

    def toByte(self):
        header = Packets.get_ack_packet_header(
            Packets, self.hopAddr, self.prevHopAddr)
        # print(str(header))
        obj = header
        print("# ---ack as byte:\t"+str(obj))
        return obj

    def toDict(self):
        obj = {}
        obj["type"] = 4
        obj["flags"] = 0
        obj["hopAddress"] = self.hopAddr
        obj["prevHopAddress"] = self.prevHopAddr
        return obj

    def toIntArray(self):
        arr = []
        _bytes = b'01000000'
        arr.append(int(_bytes, base=2))
        arr.append(self.hopAddr)
        arr.append(self.prevHopAddr)
        return arr
