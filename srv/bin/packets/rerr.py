#!/usr/bin/python3.8
from .packets import Packets as Packets
import base64


class Rerr:
    def __init__(self, hopAddress, prevHopAddr, pathCount, destinationList):
        """ destList: [{"destinationAddress":1,"destinationSequence":1}, {"destinationAddress":N,"destinationSequence":N}] """
        self.hopAddress = hopAddress
        self.prevHopAddress = prevHopAddr
        self.pathCount = pathCount
        self.destinationList = destinationList
        self.padding = 0

    def get_packet_tail(self):
        obj = b''
        for i in list(self.destinationList):
            obj = obj + Packets.int_to_bits(i["destinationAddress"], 8) + \
                Packets.int_to_bits(i["destinationSequence"], 8)
        obj = obj + Packets.int_to_bits(self.padding, 8)

    def toByte(self):
        header = Packets.get_error_packet_header(
            Packets, self.hopAddress, self.prevHopAddress)
        # print(str(header))
        obj = header + \
            Packets.int_to_bits(self.pathCount, 8) + self.get_packet_tail()
        print("# --route error as byte:\t"+str(obj))
        return obj

    def toBase64(self):
        byte_string = self.toByte()
        hex_value = Packets.get_hex(byte_string)
        print("# -route error as hex:\t"+hex_value)
        try:
            encoded = base64.b64encode(bytes.fromhex(hex_value))
        except ValueError:
            encoded = base64.b64encode(bytes.fromhex('0'+hex_value))
        print("# route error as base64:\t"+str(encoded))
        return encoded
    def toDict(self):
        obj = {}
        
        obj["type"] = 2
        obj["flags"] = 0 
        obj["hopAddress"] = self.hopAddress
        obj["prevHopAddress"] = self.prevHopAddress
        obj["pathCount"] = self.pathCount
        obj["destinationList"] = self.destinationList
        return obj

