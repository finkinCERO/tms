#!/usr/bin/python3.8
import serial
import time
import keyboard
import base64
from packets.rreq import Rreq
from packets.rrep import Rrep
from packets.msg import Msg
from packets.ack import Ack
from packets.rerr import Rerr
from utilstst import decodeBase64, encodeBase64, parse_packet
from packets.packets import Packets

from packets.rrep import Rrep

# _serial = None
ADDRESS = 2
SENDBYTE = 0
DEST_SEQ = 0
SERIAL = None


def reader(ser):

    s = ser.readline()
    de = s.decode("ascii")
    if "\r\n" in de:
        print("= receive:\t\t" + de.replace("\r\n", ""))
    else:
        print("= receive:\t\t" + s.decode("ascii"))
    return s


def send(_serial, message, dest):
    print("# -- send:\t\t" + str(message))
    m = message + "\r\n"
    _serial.write(m.encode())
    return True


def setRX(serial):
    rxMode = "AT+RX\r\n"
    print("set RX")
    serial.write(rxMode.encode())
    return True


def sender(serial):
    print("start AT test: proof of concept")
    print("-------------------------------")
    msg = Msg(111, ADDRESS, 4, 1, 1, "Hello World")
    msg_b64 = encodeBase64(msg.toIntArray()).decode("ascii") + msg.text
    send(serial, msg_b64, "FFFFF")
    # setRX(serial)
    while True:
        # text = input("send: ")
        # send(serial, text, "FFFF")
        if(serial.in_waiting > 0):
            message = reader(serial)
            handle(serial, message, SENDBYTE)
            # print("# -+ byte:\t"+str(getByte()))
        """   elif keyboard.is_pressed('<'):
            text = input("$ -[send]:\t")
            send(serial, text, "FFFFF")
        elif keyboard.is_pressed('>'):
            break """
        # if text=="exit":
        # break
    print("serial close...")
    serial.close()
    exit(1)


def setByte(number):
    global SENDBYTE
    SENDBYTE = int(number)


def getByte():
    global SENDBYTE
    return SENDBYTE


def isBase64(s):
    try:
        res = base64.b64encode(base64.b64decode(s))

        return res.decode("ascii") == s
    except Exception:
        return False


def routeReply(flags, destination):
    print("# sending route reply to" + str(destination))


def getDestSeq():
    global DEST_SEQ
    DEST_SEQ += 1
    return DEST_SEQ


def testRouteReply(packet: Rreq):
    global SERIAL
    print("# preparing test route reply")
    req_id = packet.requestId
    dest_addr = packet.destAddress
    dest_seq = packet.destSequence
    hop_count = packet.hopCount+1
    origin_addr = packet.originAddress
    origin_seq = packet.originSequence
    # output
    print("* request id:\t\t", req_id)
    print("* dest address:\t\t", dest_addr)
    print("* dest_seq:\t\t", dest_seq)
    print("* hop_count:\t\t", hop_count)
    print("* origin addr:\t\t", origin_addr)
    print("* origin seq:\t\t", origin_seq)
    reply = Rrep(111, ADDRESS, req_id, origin_addr,
                 origin_seq, 2, dest_addr, 0)
    arr = reply.toIntArray()
    message = encodeBase64(arr)
    print("# message:\t\t" + str(message))
    send(SERIAL, message.decode("ascii"), "FFFFF")


def decoding(message):
    global SERIAL
    print("# decode base64 string: " + str(message))
    rType = message[:8].encode("ascii")
    print("# type: "+str(rType))

    int_arr = decodeBase64(rType)
    request_type = int(Packets.int_to_bits(int_arr[0], 8)[0:4], base=2)
    request_flags = int(Packets.int_to_bits(int_arr[0], 8)[4:8], base=2)

    print("# 8 chars decoded:\t"+str(int_arr))

    print("(b) -request type:\t" +
          str(Packets.int_to_bits(int_arr[0], 8)[0:4]) + "as int: "+str(request_type))
    print("(b) request flags:\t" +
          str(Packets.int_to_bits(int_arr[0], 8)[4:8]))

    print(str(int_arr))
    #########################

    if request_type == 0:
        int_arr = decodeBase64(message)
        # check if route exists
        # if exists return route reply
        print("# route request detected")
        testRouteReply(parse_packet(int_arr))

    elif request_type == 1:
        int_arr = decodeBase64(message)
        # check route reply
    elif request_type == 2:
        int_arr = decodeBase64(message)
    elif request_type == 3:
        print("# msg detected")
        int_arr = decodeBase64(message[:8])
        msg = Msg(int_arr[0], int_arr[1], int_arr[2],
                  int_arr[3], int_arr[4], message[8:])
        ack = Ack(ADDRESS, ADDRESS+1)
        ack_b64 = encodeBase64(ack.toIntArray())
        send(SERIAL, ack_b64.decode("ascii"), "FFFFF")
        print("# message text:\t\t"+str(msg.text))
        print("# -decoded ack:\t\t"+str(decodeBase64(ack_b64)))
    elif request_type == 4:
        int_arr = decodeBase64(message)
        ack = parse_packet(int_arr)
        print("# ack detected: "+str(ack))
        # find message and pass to frontend
        # delete message from active message
        # reply = Rrep(ADDRESS, 2,)
        # send route reply
    # send(serial, "AT,SENDED", "111")


def handle(serial, message, byte):
    global SERIAL
    SERIAL = serial
    m = message.decode("ascii").replace("\r\n", "")
    if "AT+ADDR=" in m or "AT+CFG=" in m or "AT+RX" == m or m == "AT":
        send(serial, "AT,OK", "111")
    if "AT+DEST=" in m:
        send(serial, "AT,OK", "111")
    elif "AT+SEND=" in m:
        print("# -- byte:\t\t"+m.split("=")[1])
        setByte(m.split("=")[1])
        send(serial, "AT,OK", "111")
    else:
        if len(m) == byte:
            print("# SEND OK")
            send(serial, "AT,SENDED", "111")
        if isBase64(m[:8]):
            decoding(m)
        else:
            print("* not base base64 encoded...")


def reset():
    print("resetting modul...")
    _serial = serial.Serial()
    _serial.baudrate = 115200
    _serial.port = '/dev/ttyAMA0'
    _serial.open()
    _serial.flush()
    return _serial
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setup(18, GPIO.OUT)
    # GPIO.output(18, GPIO.HIGH)
    # time.sleep(1)
    # GPIO.output(18, GPIO.LOW)
    # GPIO.cleanup()


if __name__ == "__main__":
    serial = reset()
    print(serial.name)

    sender(serial)
