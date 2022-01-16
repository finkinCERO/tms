#!/usr/bin/python3.8
from .packets import Packets as Packets
import base64


class Rreq:
    def __init__(self, hopAddress, prevHopAddr, reqId, destAddr, destSequence, hopCount, originAddr, originSequence):
        self.hopAddress = hopAddress
        self.prevHopAddress = prevHopAddr
        self.requestId = reqId
        self.destAddress = destAddr
        self.destSequence = destSequence
        self.hopCount = hopCount
        self.originAddress = originAddr
        self.originSequence = originSequence
        #self.asBase64 = self.toBase64()

    def toDict(self):
        obj = {}
        obj["type"] = 0
        obj["flags"] = 0 
        obj["hopAddress"] = self.hopAddress
        obj["prevHopAddress"] = self.prevHopAddress
        obj["requestId"] = self.requestId
        obj["destAddress"] = self.destAddress
        obj["destSequence"] = self.destSequence
        obj["hopCount"] = self.hopCount
        obj["originAddress"] = self.originAddress
        obj["originSequence"] = self.originSequence
        return obj
    def toByte(self):

        header = Packets.get_request_packet_header(Packets,
                                                   Packets.int_to_bits(int(self.hopAddress), 8), Packets.int_to_bits(self.prevHopAddress, 8))

        obj = header + Packets.int_to_bits(self.requestId, 8) + Packets.int_to_bits(self.destAddress, 8) + Packets.int_to_bits(self.destSequence, 8) + Packets.int_to_bits(
            self.hopCount, 8) + Packets.int_to_bits(self.originAddress, 8) + Packets.int_to_bits(self.originSequence, 8)
        print("# --route request as byte:\t"+str(obj))
        return obj
    def getInfos(self):
        obj={}
        byte_string = self.toByte()
        hex_value = Packets.get_hex(byte_string)
        obj["hex"] = hex_value
        obj["bytes"] = byte_string
        return obj
    def toBase64(self):
        byte_string = self.toByte()
        hex_value = Packets.get_hex(byte_string)
        print("# ---route request as hex:\t"+hex_value)
        try:
            encoded = base64.b64encode(bytes.fromhex(hex_value))
        except ValueError:
            print("# ---------hex correction:\t"+'0'+hex_value)
            encoded = base64.b64encode(bytes.fromhex('0'+hex_value))
        print("# route request as base64:\t"+str(encoded))
        return encoded

    def toIntArray(self):
        arr = []
        _bytes = self.toByte()
        arr.append(int(_bytes[0:8], base=2))
        arr.append(self.hopAddress)
        arr.append(self.prevHopAddress)
        arr.append(self.requestId)
        arr.append(self.destAddress)
        arr.append(self.destSequence)
        arr.append(self.hopCount)
        arr.append(self.originAddress)
        arr.append(self.originSequence)
        return arr
