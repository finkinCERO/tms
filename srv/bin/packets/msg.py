#!/usr/bin/python3.8
from .packets import Packets as Packets
import base64
import time


class Msg:
    def __init__(self, hopAddress, prevHopAddress, destAddress, originSequence, msgId, text):
        self.viewType = "default"
        self.hopAddress = hopAddress
        self.prevHopAddress = prevHopAddress
        self.destAddress = destAddress
        self.originSequence = originSequence
        self.messageId = msgId
        self.text = text
        self.active = False
        self.timestamp = time.time()*1000.0
        self.count = 0

    def toByte(self):
        header = Packets.get_msg_packet_header(
            Packets, Packets.int_to_bits(self.hopAddress, 8), Packets.int_to_bits(self.prevHopAddress, 8))
        # print(str(header))
        obj = header + Packets.int_to_bits(self.destAddress, 8) + Packets.int_to_bits(self.originSequence, 8) + Packets.int_to_bits(self.messageId, 8) \
            + str(self.text).encode("ascii")
        print("# ---msg as byte:\t"+str(obj))
        return obj

    def toBase64(self):
        byte_string = self.toByte()
        hex_value = Packets.get_hex(byte_string)
        print("# ----msg as hex:\t"+hex_value)
        try:
            encoded = base64.b64encode(bytes.fromhex(hex_value))
        except ValueError:
            encoded = base64.b64encode(bytes.fromhex('0'+hex_value))
        print("# -msg as base64:\t"+str(encoded))
        return encoded

    def toDict(self):
        obj = {}
        obj["name"] = "message"
        obj["viewType"] = self.viewType
        obj["type"] = 3
        obj["flags"] = 0
        obj["hopAddress"] = self.hopAddress
        obj["prevHopAddress"] = self.prevHopAddress
        obj["destAddress"] = self.destAddress
        obj["originSequence"] = self.originSequence
        obj["messageId"] = self.messageId
        obj["count"] = self.count
        obj["timestamp"] = self.timestamp
        try:
            obj["text"] = self.text.decode("ascii")
        except:
            obj["text"] = self.text
        return obj

    def toIntArray(self):
        arr = []
        _bytes = Packets.get_msg_packet_header(
            Packets, Packets.int_to_bits(self.hopAddress, 8), Packets.int_to_bits(self.prevHopAddress, 8))
        arr.append(int(_bytes[0:8], base=2))
        arr.append(self.hopAddress)
        arr.append(self.prevHopAddress)
        arr.append(self.destAddress)
        arr.append(self.originSequence)
        arr.append(self.messageId)
        return arr

    def getTxtIntArr(self):
        arr = self.txtToBinary(self.text)
        arr_result = []
        for i in list(arr):
            arr_result.append(int(str(i), base=2))
        print(arr)
        return arr_result
        # arr.append(str(self.text).encode("ascii"))

    def txtToBinary(self, txt):
        l, m = [], []
        for i in txt:
            l.append(ord(i))
        for i in l:
            m.append(int(bin(i)[2:]))
        return m
