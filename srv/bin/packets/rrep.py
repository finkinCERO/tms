#!/usr/bin/python3.8
from .packets import Packets as Packets
import base64


class Rrep:
    def __init__(self, hopAddress, prevHopAddr, requestId, destAddr, destSequence, hopCount, originAddr, originSequence):
        self.hopAddress = hopAddress
        self.prevHopAddress = prevHopAddr
        self.requestId = requestId
        self.destAddress = destAddr
        self.placeholder = 0
        self.destSequence = destSequence
        self.hopCount = hopCount
        self.originAddress = originAddr
        self.originSequence = originSequence

    def toByte(self):
        header = Packets.get_reply_packet_header(
            Packets, self.hopAddress, self.prevHopAddress)
        # print(str(header))
        obj = header + Packets.int_to_bits(self.requestId, 8) + Packets.int_to_bits(self.destAddress, 8) + Packets.int_to_bits(
            self.destSequence, 8) + Packets.int_to_bits(self.hopCount, 8) + Packets.int_to_bits(self.originAddress, 8) + Packets.int_to_bits(0, 8)
        print("# --route reply as byte: "+str(obj))
        return obj

    def toBase64(self):
        byte_string = self.toByte()
        hex_value = Packets.get_hex(byte_string)
        print("# ---route reply as hex: "+hex_value)
        try:
            encoded = base64.b64encode(bytes.fromhex(hex_value))
        except ValueError:
            print("# -hex correction: "+'0'+hex_value)
            encoded = base64.b64encode(bytes.fromhex('0'+hex_value))
        print("# route reply as base64: "+str(encoded))
        return encoded

    def getInfos(self):
        obj = {}
        byte_string = self.toByte()
        hex_value = Packets.get_hex(byte_string)
        obj["hex"] = hex_value
        obj["bytes"] = byte_string
        return obj

    def toDict(self):
        obj = {}
        obj["type"] = 1
        obj["flags"] = 0
        obj["hopAddress"] = self.hopAddress
        obj["prevHopAddress"] = self.prevHopAddress
        obj["requestId"] = self.requestId
        obj["destinationAddress"] = self.destAddress
        obj["destinationSeqence"] = self.destSequence
        obj["hopCount"] = self.hopCount
        obj["originAddress"] = self.originAddress
        obj["originSequence"] = self.originSequence
        return obj

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
        

