#!/usr/bin/python3.8
from .packets import Packets as Packets
import base64
from .path import Path


class Rerr:
    def __init__(self, hopAddress, prevHopAddr, pathCount, destinationList):
        """ destList: [{"destAddress":1,"destSequence":1}, {"destAddress":N,"destSequence":N}] """
        self.hopAddress = hopAddress
        self.prevHopAddress = prevHopAddr
        self.pathCount = pathCount
        self.destinationList = destinationList
        self.padding = 0

    def get_packet_tail(self):
        obj = b''
        for i in list(self.destinationList):
            obj = obj + Packets.int_to_bits(i["destAddress"], 8) + \
                Packets.int_to_bits(i["destSequence"], 8)
        obj = obj + Packets.int_to_bits(self.padding, 8)

    def toByte(self):
        header = Packets.get_error_packet_header(
            Packets, self.hopAddress, self.prevHopAddress)
        # print(str(header))
        obj = header + \
            Packets.int_to_bits(self.pathCount, 8) + self.get_packet_tail()
        print("# --route error as byte:\t"+str(obj))
        return obj

    def getHeaderByte(self):
        return Packets.get_error_packet_header(
            Packets, self.hopAddress, self.prevHopAddress)

    def toDict(self):
        obj = {}

        obj["type"] = 2
        obj["flags"] = 0
        obj["hopAddress"] = self.hopAddress
        obj["prevHopAddress"] = self.prevHopAddress
        obj["pathCount"] = self.pathCount
        obj["destinationList"] = []
        print("######################")
        print("######################")
        print("######################")
        print("######################")
        print("list: "+str(self.destinationList))
        for i in list(self.destinationList):
            obj["destinationList"].append(i.toDict())
        return obj

    def toIntArray(self):
        arr = []
        _bytes = self.getHeaderByte()
        arr.append(int(_bytes[0:8], base=2))
        arr.append(self.hopAddress)
        arr.append(self.prevHopAddress)
        arr.append(self.pathCount)
        for obj in list(self.destinationList):
            arr.append(int(obj.destAddress))
            arr.append(int(obj.destSequence))
        arr.append(0)
        return arr
