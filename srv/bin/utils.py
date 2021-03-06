#!/usr/bin/python3.8
import os
import json

from .packets.path import Path
from .packets.rreq import Rreq
import base64
from .packets.rrep import Rrep
from .packets.msg import Msg
from .packets.rerr import Rerr
from .packets.ack import Ack
from .packets.packets import Packets
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
# BASE 64 STUFF
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

def isBase64(s):
    try:
        res = base64.b64encode(base64.b64decode(s))

        return res.decode("ascii") == s
    except Exception:
        return False

# Parse Int Array to packet-object
# returns a packet obj
# payload only for message packet
def parse_packet(int_arr, payload=None):
    type_and_flags = Packets.int_to_bits(int_arr[0], 8)
    _type = int(type_and_flags[0:4], base=2)
    _flags = int(type_and_flags[4:8], base=2)
    obj = None
    write_log("# parse packet:\t"+str(int_arr))
    if _type == 0:
        return Rreq(int_arr[1], int_arr[2], int_arr[3], int_arr[4],
                    int_arr[5], int_arr[6], int_arr[7], int_arr[8])
    elif _type == 1:
        return Rrep(int_arr[1], int_arr[2], int_arr[3], int_arr[4],
                    int_arr[5], int_arr[6], int_arr[7], int_arr[8])
    elif _type == 2:
        # route error
        hop = int_arr[1]
        prevHop = int_arr[2]
        pathCount = int_arr[3]
        sequences = int_arr[4:]
        sequences = sequences[:len(sequences)-1]
        write_log("= 1. parsing route error: "+str(sequences))
        seq = []
        i = 0
        last = None
        write_log("= seq arr length: "+str(len(sequences)))
        for sequence in list(sequences):
            write_log("* last: "+str(last) + "\t| seq: "+str(sequence))
            if i % 2 == 0:
                last = sequence
            elif i % 2 == 1:
                p = Path(int(last), int(sequence))
                write_log("# add sequence: " + str(p.toDict()))
                seq.append(p)
            i += 1
        write_log("= parsing route error: "+str(sequences))
        write_log("= parsing route error: "+str(seq))
        return Rerr(hop, prevHop, pathCount, seq)

    elif _type == 3:
        # message
        write_log("= parsing msg")
        return Msg(int_arr[1], int_arr[2], int_arr[3],
                   int_arr[4], int_arr[5], payload)

    elif _type == 4:
        # ack
        write_log("= parsing ack")
        return Ack(int_arr[1], int_arr[2])
    return obj
    # ...
