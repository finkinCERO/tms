#!/usr/bin/python3.8

import base64

from packets.rreq import Rreq
from packets.rrep import Rrep
from packets.packets import Packets
from utilstst import decodeBase64, encodeBase64, parse_packet
from packets.msg import Msg




b = b"000000001111111100000100000000110000010100000110000001110000001000000010"
c = Packets.get_hex(b)
d = Packets.hex_to_binary_bits(Packets, c)
#print(b)
#print(c)
#print(d.encode("ascii"))

print("##################")
#reply = Rrep(3, 4, 3, 5, 6, 7, 2, 2)
#request = Rreq(255, 4, 3, 5, 6, 7, 2, 2)

# pack0.toBase64()
#b = request.toBase64()
#c = request.toDict()
#print(c)
#print(b)
#b64_str = 'AP8EAwUGBwIC'
#arr = decodeBase64(b64_str)
#print(arr)
#result_b64 = encodeBase64(arr[0], arr[1], arr[2], arr[3],
#                          arr[4], arr[5], arr[6], arr[7], arr[8])

#print(request.toIntArray())



msg = Msg(3,4,5,1,1,"hello world")

msgArr = msg.toIntArray()
print(msgArr)

msg_b64 = encodeBase64(msgArr)
msg_decoded = decodeBase64(msg_b64)
print(msg_decoded)


o = parse_packet(msg_decoded)
print(o.text)