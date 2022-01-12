#!/usr/bin/python3.8
import os
import json
from packets.rreq import Rreq
import base64
from packets.rrep import Rrep
from packets.msg import Msg
from packets.rerr import Rerr
from packets.ack import Ack
from packets.packets import Packets
dirname = os.path.dirname(__file__)
log_file = os.path.join(dirname, '../log/service.log')

# print(dirname)
# print(log_file)


def write_log(msg):
    global log_file
    f = open(log_file, "a+")
    f.write(msg+'\n')
    f.flush()
    f.close()


def toBinary(txt):
    l, m = [], []
    for i in txt:
        l.append(ord(i))
    for i in l:
        m.append(int(bin(i)[2:]))
    return m



def prepareRouteRequest(obj):
    """[summary]

    Args:
        obj (dict): objects contains destination, 
    """
    print()

    # return


    

def decodeBase64(b64_string):
    _bytes = base64.b64decode(b64_string)
    int_arr = [x for x in _bytes]
    return int_arr


def encodeBase64(int_arr):
    byte_arr = b''
    for value in int_arr:
        byte_arr += int(value).to_bytes(1, 'big')
    result = base64.b64encode(byte_arr)
    print(result)
    return result



def create_reply_from_binary(binary):
    reply = Rrep(int(binary[8:16], base=2), int(
        binary[16:24], base=2), int(
            binary[24:32], base=2), int(binary[32:40], base=2), int(
                binary[40:48], base=2), int(binary[48:56], base=2), int(binary[56:64], base=2), int(binary[64:72], base=2))
    return reply


def parse_packet(int_arr, payload=None):
    type_and_flags = Packets.int_to_bits(int_arr[0], 8)
    _type = int(type_and_flags[0:4], base=2)
    _flags = int(type_and_flags[4:8], base=2)
    obj = None
    if _type == 0:
        obj = Rreq(int_arr[1], int_arr[2], int_arr[3], int_arr[4],
                   int_arr[5], int_arr[6], int_arr[7], int_arr[8])
    elif _type == 1:
        obj = Rrep(int_arr[1], int_arr[2], int_arr[3], int_arr[4],
                   int_arr[5], int_arr[6], int_arr[7], int_arr[8])
    elif _type == 2:
        # route error

        print("parsing route error")
    elif _type == 3:
        # message
        obj = Msg(int_arr[1], int_arr[2], int_arr[3],
                  int_arr[4], int_arr[5], payload)

        print("= parsing msg: "+str(obj.toDict()))
    elif _type == 4:
        # ack
        print("parsing ack")
        obj = Ack(int_arr[1], int_arr[2])
    return obj
    # ...
