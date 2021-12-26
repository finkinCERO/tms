#!/usr/bin/python3.8
from packets import Packets as Packets
import base64


class Rreq:
    def __init__(self, hopAddress, prevHopAddr, reqId, destAddr, destSequence, hopCount, originAddr, originSequence):
        self.hopAddr = hopAddress
        self.prevHopAddr = prevHopAddr
        self.reqId = reqId
        self.destAddress = destAddr
        self.destSequence = destSequence
        self.hopCount = hopCount
        self.originAddress = originAddr
        self.originSequence = originSequence
        self.asBase64 = self.toBase64()

    def toByte(self):

        header = Packets.get_request_packet_header(Packets,
                                                   Packets.int_to_bits(int(self.hopAddr), 8), Packets.int_to_bits(self.prevHopAddr, 8))

        obj = header + Packets.int_to_bits(self.reqId, 8) + Packets.int_to_bits(self.destAddress, 8) + Packets.int_to_bits(
            self.hopCount, 8) + Packets.int_to_bits(self.originAddress, 8) + Packets.int_to_bits(self.originSequence, 8)
        print(str(obj))
        return obj

    def toBase64(self):
        byte_string = self.toByte()
        as_hex = hex(int(byte_string, base=2))
        print("hex\t->\t"+as_hex)
        return base64.b64encode(bytes.fromhex(as_hex[2:]))
    
    

# TEST
r = Rreq(255, 111, 1, 64, 1, 0, 111, 1)
#print(str(r.toByte()))
#print(str(r.toBase64()))
