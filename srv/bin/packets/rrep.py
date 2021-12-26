#!/usr/bin/python3.8
from packets import Packets as Packets


class Rrep:
    def __init__(self, hopAddress, prevHopAddr, reqId, destAddr, destSequence, hopCount, originAddr, originSequence):
        self.hopAddr = hopAddress
        self.prevHopAddr = prevHopAddr
        self.reqId = reqId
        self.destAddress = destAddr
        self.destSequence = destSequence
        self.hopCount = hopCount
        self.originAddress = originAddr
        self.originSequence = originSequence

    def toByte(self):
        header = Packets.get_request_packet_header(
            self.hopAddr, self.prevHopAddr)
        obj = header + Packets.int_to_bits(self.reqId, 8) + Packets.int_to_bits(self.destAddress, 8) + Packets.int_to_bits(
            self.hopCount, 8) + Packets.int_to_bits(self.originAddress, 8) + Packets.int_to_bits(self.originSequence, 8)
        print(str(obj))
        return obj

    def toBase64(self):
        return 0

