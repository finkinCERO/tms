#!/usr/bin/python3.8
from asyncore import write
from email import message
from glob import glob
from sys import stdout, stdin
import sys
import traceback
import uuid
import threading
from time import sleep
import json
import os
import serial
import random
import time
import select
from bin.utils import create_reply_from_binary, isBase64, parse_packet, encodeBase64, decodeBase64, write_log
from bin.packets.rreq import Rreq
import time
from bin.packets.rrep import Rrep
from bin.packets.msg import Msg
from bin.packets.rerr import Rerr
from bin.packets.ack import Ack
from bin.packets.packets import Packets
user = None
# CONFIG = "433000000,5,6,12,4,1,0,0,0,0,3000,8,8"
CONFIG = "433920000,5,6,12,4,1,0,0,0,0,3000,8,8"
ADDRESS = "111"
SERIAL = None
BAUD = 115200
# rfcomm0
PORT = "/dev/ttyS0"
ROUTES = []
REVERSEROUTES = []
SEQ_NUM = 0
DEST_SEQ_NUM = -1
REQ_ID = -1
ACTIVE_REQUESTS = {"rreq": [], "rrep": [], "msg": [], "ack": [], "rerr": []}
MSG_ID = -1


def save_file(path, data):
    _path = get_path_to_objects() + "obj/export/"+path
    with open(_path, 'w') as f:
        json.dump(data, f)


# --- --------------------------------------------------------------------------


# --- --------------------------------------------------------------------------


# --- --------------------------------------------------------------------------

def get_ticker():
    return random.randint(30, 300)/1000


def send_out(msg):
    """
    sends message trough std out, websocket daemon
    can pass to frontend connection
    (push messages without request to frontend or as a reaction to a request)

    :param msg: msg to send out
    :type path: str
    :rtype: True | None
    """
    # send string to web page
    write_log("# [sending std out]: "+str(msg))
    # write_log(str(msg))
    stdout.write(str(msg)+'\n')
    stdout.flush()

# --- --------------------------------------------------------------------------


def get_request_id():
    global REQ_ID
    REQ_ID += 1
    if REQ_ID == 256:
        REQ_ID = 1
    return REQ_ID


def get_msg_id():
    global MSG_ID
    MSG_ID += 1
    if MSG_ID == 256:
        MSG_ID = 0
    return MSG_ID


def get_sequence_number():
    global SEQ_NUM
    SEQ_NUM += 1
    if SEQ_NUM == 256:
        SEQ_NUM = 1
    return SEQ_NUM


def get_dest_sequence_number():
    global DEST_SEQ_NUM
    DEST_SEQ_NUM += 1
    if DEST_SEQ_NUM == 256:
        DEST_SEQ_NUM = 1
    return DEST_SEQ_NUM


def clear_routes():
    global ROUTES
    global REVERSEROUTES
    ROUTES = []
    REVERSEROUTES = []


def handle_Rrep(data):

    write_log("# handle route reply")


def get_obj_from_list_by(list, param, key: str):
    for obj in list:
        if obj[key] == param:
            return obj
    return None


def get_route_by(param, key: str):
    global ROUTES
    r = get_obj_from_list_by(ROUTES, param, key)
    if r != None and r["isValid"] == False:
        return None
    return r


def get_reverse_route_by(param, key: str):
    global REVERSEROUTES
    return get_obj_from_list_by(REVERSEROUTES, param, key)


def get_route(address):
    route = get_route_by(int(address), "destination")
    if(route != None):
        write_log("# route found:\t\t\t\t"+str(route))
        return route

    write_log("# no route found:\t\t\t\t"+str(address))
    return None


def find_message(rrep: Rrep):
    global ACTIVE_REQUESTS
    write_log("* active requests: "+str(ACTIVE_REQUESTS))
    for obj in list(ACTIVE_REQUESTS["msg"]):
        if(rrep.requestId == obj.messageId):
            return obj
    return None


def add_route(obj):
    global ROUTES

    route = get_route(obj["destination"])
    if route != None:
        if route["metric"] == obj["metric"] and route["nextHop"] == obj["nextHop"]:
            return False
    ROUTES.append(obj)
    response = open_json("table-wrapper.json")
    response["data"] = ROUTES
    send_out(json.dumps(response))
    write_log("# route added: "+str(obj))

    return True


def check_reverse_route(id, origin):
    global REVERSEROUTES
    for obj in list(REVERSEROUTES):
        if obj["requestId"] == id and obj["source"] == origin:
            return True
    return False


def add_reverse_route(obj):
    global REVERSEROUTES
    routes = []
    if len(REVERSEROUTES) == 0:
        REVERSEROUTES.append(obj)
    for i in list(REVERSEROUTES):
        if obj["destination"] != i["destination"]:
            routes.append(i)
        elif obj["destination"] == i["destination"] and obj["metric"] < i["metric"]:
            routes.append(obj)
        else:
            routes.append(i)
    REVERSEROUTES = routes
    write_log("(add) reverse routes: "+str(REVERSEROUTES))
    response = open_json("table-wrapper.json")
    response["name"] = "reverse-routing-table"
    response["data"] = REVERSEROUTES
    send_out(json.dumps(response))
    # write_log("# reverse route added")
    return True


def send(serial, message, dest):
    m = "AT+DEST=" + dest + "\r\n"

    serial.write(m.encode())
    if verify_module_return(serial):
        print("# length\t\t->\t"+str(len(message)))
        sendMode = "AT+SEND="+str(len(message))+"\r\n"
        write_log("# [set send mode]:\t"+sendMode +
                  "# [message]\t\t->\t"+str(message))

        serial.write(sendMode.encode())
        if(verify_module_return(serial)):
            write_log("* AT return verified, sending message")
            m = message.decode("ascii") + "\r\n"
            serial.write(m.encode())
            verify_module_return(serial)
            return True
        else:
            return False
    else:
        return False


def set_rx(serial):
    rxMode = "AT+RX\r\n"
    serial.write(rxMode.encode())
    write_log("# set RX")
    time.sleep(0.1)
    return True


def sender():
    set_rx(SERIAL)
    while True:
        if(verify_module_return(SERIAL) and SERIAL.in_waiting > 0):
            reader(SERIAL)


def reader(ser):
    s = ser.readline()
    # print(s)
    write_log("# read message: "+str(s))
    # send message trought websocket...

    return s.replace(b"\r\n", b"")

def config(serial, address, _config):
    # set address
    global ADDRESS
    try:
        ADDRESS = int(address)
        addr = "AT+ADDR="+address+"\r\n"
        serial.write(addr.encode())

        time.sleep(0.05)
        # config
        if(verify_module_return(serial)):
            CONFIG = _config
            c = "AT+CFG="+_config+"\r\n"
            serial.write(c.encode())
        return True
    except:
        write_log("# config failed")
        return False


def verify_module_return(serial):
    global ADDRESS
    global CONFIG
    global BAUD
    global PORT
    time.sleep(random.randint(150, 200)/1000)
    status = reader(serial)
    print("# verify status of module:\t"+status.decode("ascii"))
    if(status == b'AT,OK\r\n' or status == b'AT,OK\n'):
        return True
    elif(status == b'AT,OKERR:CPU_BUSY\r\n'):
        _serial = reset(BAUD, PORT)
        config(_serial, ADDRESS, CONFIG)
        return False
    elif(status == b'AT,SENDED\r\n'):
        return True
    elif(status == b'AT,SENDING\r\n'):
        write_log("# sending...")
    elif (status == b'\r\n' or status == ''):
        write_log("# empty read, verifying")
        return True
    else:
        write_log("# ignoring return of module: "+str(status))
        return True


def reset(baud, port):
    write_log("# init module port: "+port+" | baud:"+str(baud))
    global BAUD
    global PORT
    global SERIAL
    BAUD = baud
    PORT = port
    _serial = serial.Serial()
    _serial.baudrate = baud  # 115200
    # _serial.port = '/dev/rfcomm0'
    _serial.timeout = 5
    _serial.port = port  # '/dev/ttyS0'
    try:
        _serial.open()
        _serial.flush()
        # config(_serial)
        SERIAL = _serial
        # send(SERIAL, "Hello, i´m Davis [init]", "FFFFF")
        return _serial
    except:
        _error = open_json("error.json")
        _error["message"] = "Error occured during initialisation, please check port permissions of host, port name or if valid baudrate is setted"
        send_out(json.dumps(_error))
        write_log("# module init error (reset failed)")
        return None


def create_route_obj(dest, next_hop, precursors, metric, seq_num, is_valid: bool):
    route = open_json("routing-table.json")
    route["destination"] = dest
    route["nextHop"] = next_hop
    route["precursors"] = precursors
    route["metric"] = metric
    route["sequenceNumber"] = seq_num
    route["isValid"] = is_valid
    return route


def create_reverse_route_obj(dest, source, id, metric, prevHop):
    r_route = open_json("reverse-routing-table.json")
    r_route["destination"] = dest
    r_route["source"] = source
    r_route["requestId"] = id
    r_route["metric"] = metric
    r_route["prevHop"] = prevHop
    return r_route


def pass_msg(msg):
    global BAUD
    global PORT
    _msg = msg.decode("ascii")
    if _msg == 'AT,OK' or _msg == "AT,SENDED" or _msg == "AT,SENDING" or _msg == "":
        write_log("# msg not passed")
        return False
    elif _msg == "AT,OKERR:CPU_BUSY":
        reset(BAUD, PORT)
        return False
    write_log("# msg passing: "+str(msg) + " as string:"+_msg)
    return True


def pop_message():
    global ACTIVE_REQUESTS
    if len(ACTIVE_REQUESTS["msg"])>0:
        ACTIVE_REQUESTS["msg"].pop(0)


def serve():
    """
    listening on std in,
    std in messages -> json string
    """
    global ADDRESS
    exit_cmd = 'exit'
    # global passphrase
    wrong_message_counter = 0
    write_log("# start server")
    _SERIAL = None
    _switch = False
    while True:
        # Websocket:
        requestRaw = ""
        # check if line should be readed from stdin
        if select.select([sys.stdin, ], [], [], 0.0)[0]:
            requestRaw = stdin.readline()
        # procceed client messages
        if requestRaw != "":
            write_log("# client request\t\t->\t"+requestRaw)
            request = json.loads(requestRaw)

            # ----------------------------------------------------
            # module settings
            if(request["name"] == "reset-module"):
                _SERIAL = reset(request["baud"], request["port"])
                if _SERIAL != None:
                    send_out(json.dumps(open_json("reset.json")))
                # SERIAL shouldn't be used after resetting, waiting for config -> _switch = True
                _switch = False
            elif(request["name"] == "set-config"):
                if _SERIAL != None:
                    write_log("# entering config")
                    config(_SERIAL, request["address"], request["config"])
                    send_out(json.dumps(open_json("set-config.json")))
                    _switch = True
                    clear_routes()
                    add_route(create_route_obj(
                        ADDRESS, ADDRESS, "", 0, 0, True))
                    # send(SER, "init", "FFFFF")
                    sleep(0.1)
                    set_rx(_SERIAL)
                else:
                    write_log("# serial isn't initialised")
            # ----------------------------------------------------
            # client messages
            else:
                write_log("# handle client messages\t->\t"+requestRaw)
                handle_client_messages(request, _SERIAL)
        elif _switch == True:
            # incoming messages from module
            if(_SERIAL.in_waiting > 0):
                write_log("# in waiting: "+str(_SERIAL.in_waiting))
                msg = reader(_SERIAL)
                write_log("# msg: " + str(msg))
                if pass_msg(msg):
                    # sendMessageObj(msg)

                    if b'LR' in msg:
                        write_log("# split message")
                        m = msg.decode("ascii").split(",")[
                            3].encode("ascii")
                        decoding_process(m)
                    else:
                        decoding_process(msg)

            elif (time.time()*1000.0 - LAST_CHECK) > 4999:
                check_messages()

        else:
            sleep(1)
            write_log("# NO ACTION")


def get_by_value(key, value, arr):
    _arr = []
    for i in arr:
        if i.toDict()[key] == value:
            _arr.append(i)
    return _arr


def handle_route_request(rreq: Rreq):
    global ACTIVE_REQUESTS
    global ADDRESS
    global SERIAL
    write_log("# handle route request:\t\t"+str(rreq.toDict()))
    from_addr = rreq.originAddress
    # ignore echo route request
    if from_addr == int(ADDRESS):
        write_log("# ignoring echo route request")
        return False
    prev_hop = rreq.prevHopAddress
    dest_addr = rreq.destAddress
    id = rreq.requestId
    rreq.hopCount += 1
    count = rreq.hopCount

    write_log("# no request exists")

    # ignore request if known
    if(check_reverse_route(rreq.requestId, rreq.originAddress)):
        write_log("# reverse route updates")
        return False
    # create reverse route json object & add to list
    r_route = create_reverse_route_obj(
        rreq.destAddress, rreq.originAddress, rreq.requestId, rreq.hopCount, rreq.prevHopAddress)
    add_reverse_route(r_route)
    write_log("# reverse route: "+str(r_route))
    # check if you know a route to dest address
    route = get_route(dest_addr)
    if route != None:
        rrep = Rrep(rreq.hopAddress, int(ADDRESS), rreq.requestId,
                    rreq.destAddress, rreq.destSequence, 0 + int(route["metric"]), int(ADDRESS),0)
        rrep_b64 = encodeBase64(rrep.toIntArray())
        send(SERIAL, rrep_b64, "FFFFF")
        obj = open_json("message-obj.json")
        obj["message"] = "# (reply) known route asked: " + \
            str(route["destination"])+", next hop: " + str(route["nextHop"])
        send_out(json.dumps(obj))
    else:
        write_log("# unknown rreq: "+str(rreq.toDict()))
        write_log("# broadcasting route request for path to: " +
                  str(rreq.destAddress))
        encoded = encodeBase64(rreq.toIntArray())
        write_log("# encoded rreq: "+str(encoded))
        send(SERIAL, encoded, "FFFFF")
    # add route to origin if you
    # if route == None:
    #    route = create_route_obj(
    #        from_addr, rreq.prevHopAddress, rreq.prevHopAddress, rreq.hopCount, rreq.originSequence, True)
    #    add_route(route)

        # ACTIVE_REQUESTS["rrep"].append(rreq)
        # check if route to origin exsists -> no: add route to routin table
        # check if dest route is own address -> yes: send route reply
        #

PRE = []

def set_invalid_routes(rerr: Rerr):
    global ROUTES
    global PRE
    pre = []
    for route in list(ROUTES):
        write_log("# (SET INVALID) route: "+str(route))
        for path in list(rerr.destinationList):
            write_log("# path: "+str(path.toDict()))
            if int(route["destination"]) == int(path.destAddress) and int(route["sequenceNumber"]) == int(path.destSequence):
                route["isValid"] = False
                write_log("# set invalid")
                write_log("# route: "+ str(route))
                write_log("# routes: "+ str(ROUTES))
                if route["precursors"] != "" and route["precursors"] != None:
                    write_log("# append precursor to list of node addresses which must be informed about route error.")
                    pre.append(int(route["precursors"]))
    
    write_log("# routes result: "+ str(ROUTES))
    response = open_json("table-wrapper.json")
    response["data"] = ROUTES
    send_out(json.dumps(response))
    response = open_json("error.json")
    response["message"] = "Last message failed, route error."
    send_out(json.dumps(response))       
    obj = {}
    obj["rerr"] = rerr
    obj["pre"] = pre
    PRE.append(obj)
    if len(PRE[0]["pre"]) != 0:
        rerr.prevHopAddress = int(ADDRESS)
        rerr.hopAddress = int(PRE[0]["pre"][0])
        send(SERIAL, encodeBase64(rerr.toIntArray()),"FFFFF")
    
        
def handle_ack_error(ack: Ack):
    global PRE
    global ADDRESS
    global SERIAL
    rerr = PRE[0]["rerr"]
    pre = PRE[0]["pre"]
    i = 0
    if len(pre) == 0:
        PRE.pop(0)
        return False
    for p in list(pre):
        if ack.prevHopAddr == int(p):
            PRE[0]["pre"].pop(i)
        i += 1
    if len(PRE[0]["pre"]) != 0:
        rerr.prevHopAddress = int(ADDRESS)
        rerr.hopAddress = int(PRE[0]["pre"][0])
        send(SERIAL, encodeBase64(rerr.toIntArray()), "FFFFF")
        


def handle_route_error(rerr: Rerr):
    set_invalid_routes(rerr)
    #routes = get_by_value("nextHop", )


def decoding_process(msg):
    global PRE
    write_log("# decode base64 string: " + msg.decode("ascii"))
    if "LR," in msg.decode("ascii")[:2] or "AT" == msg.decode("ascii")[:2]:
        write_log("# no base64 or not right splitted")
        return False
    rType = msg.decode("ascii")[:4].encode("ascii")
    # write_log("# type: "+str(rType))
    # _hex = Packets.base64_to_hex(msg)
    # write_log("# hex:\t\t" + _hex)
    # _bin = Packets.hex_to_binary_bits(Packets, _hex)
    # write_log(_bin)
    int_arr = decodeBase64(rType)
    write_log(str(int_arr))
    request_type = int(Packets.int_to_bits(int_arr[0], 8)[0:4], base=2)
    request_flags = int(Packets.int_to_bits(int_arr[0], 8)[4:8], base=2)

    write_log("*  request type:\t" + str(request_type))
    write_log("* request flags:\t" + str(request_flags))
    write_log("* --------------")

    write_log(str(int_arr))
    if request_type == 0:
        req = parse_packet(decodeBase64(msg))
        write_log("# rreq to dict:"+str(req.toDict()))
        handle_route_request(req)
        # check if route exists
        # if exists return route reply

    elif request_type == 1:
        write_log("# route reply detected")
        handle_reply(parse_packet(decodeBase64(msg)))
        # check route reply
    elif request_type == 2:
        write_log("# route error detected")
        rerr = parse_packet(decodeBase64(msg))
        ACTIVE_REQUESTS["rerr"].append(rerr)
        write_log("# -------- route error: "+str(rerr.toDict()))
        ack = Ack(rerr.prevHopAddress, int(ADDRESS))
        ack_b64 = encodeBase64(ack.toIntArray())
        send(SERIAL,ack_b64,"FFFFF")
        handle_route_error(rerr)
        # check if error is for you
        # fill sequence und pass
    elif request_type == 3:
        write_log("# message detected")
        handle_message(parse_packet(decodeBase64(msg[:8]), msg[8:]))
    elif request_type == 4:
        int_arr = decodeBase64(msg)
        ack = parse_packet(int_arr)
        write_log("# ack: "+str(ack.toDict()))
        if ack.hopAddr == int(ADDRESS):
            try:
                if len(PRE) == 0:
                    write_log("# Active Requests: "+str(ACTIVE_REQUESTS))
                    m = ACTIVE_REQUESTS["msg"][0]
                    send_out(json.dumps(m.toDict()))
                    pop_message()
                else:
                    write_log("# ack for rerr")
                    handle_ack_error(ack)
            except:
                write_log("# ERROR Active Requests: "+str(ACTIVE_REQUESTS))
        else:
            write_log("# ignoring ACK for hop address: "+str(ack.hopAddr))
            return False
        write_log("# ack detected")
        # find message and pass to frontend
        # delete message from active message

    write_log("# decoding process finished.")
    write_log("# --------------------------")


def is_route_valid(reply: Rrep) -> bool:
    global ACTIVE_REQUESTS
    active_route_req = ACTIVE_REQUESTS["rreq"]
    return True


LAST_CHECK = time.time()*1000.0


def process_active_message(msg: Msg):
    global ACTIVE_REQUESTS
    global ADDRESS
 
    if msg.destAddress == int(ADDRESS):
        send_out(json.dumps(msg.toDict()))
        ACTIVE_REQUESTS["msg"].pop(0)
    elif msg.count == 0 or (msg.count < 3 and (time.time()*1000.0 - msg.timestamp) > 2999):
        msg.timestamp = time.time()*1000.0
        msg.count += 1
        route = find_route(msg.destAddress)
        if route != None and route["isValid"]:
            execute_message(msg, route)
            send_out(json.dumps(msg.toDict()))
            ACTIVE_REQUESTS["msg"].pop(0)
        else:
            write_log("# route error to: "+str(msg.destAddress))
        return True
    elif msg.count >= 3:
        obj = open_json("error.json")
        obj["message"] = "message to " + \
           str(msg.destAddress) + " failed. Message: "+msg.text
        send_out(json.dumps(obj))
        ACTIVE_REQUESTS["msg"].pop(0)
        # create route error and send
        # delete route to destination where hop address is msg.hopAddress
        return False


def check_messages():
    global ACTIVE_REQUESTS
    msgs = ACTIVE_REQUESTS["msg"]
    # write_log()
    sleep(random.randint(10, 100)/1000)
    
    try:
        if msgs[0] != None:
            msg = msgs[0]
            write_log("# inwaiting message: "+str(msg.toDict()))
            return process_active_message(msg)
    except IndexError:

        return False
    return False


def execute_message(msg: Msg, route):
    write_log("# preparing execution of msg to route: "+str(route))
    global ADDRESS
    global SERIAL
    msg.hopAddress = int(route["nextHop"])
    msg.prevHopAddress = int(ADDRESS)
    int_arr = msg.toIntArray()
    msg_b64 = encodeBase64(int_arr)
    msg_b64 += msg.text
    write_log("# message:\t\t"+str(msg_b64))
    write_log("# to string:\t\t"+str(msg.toDict()))
    send(SERIAL, msg_b64, "FFFFF")
    return True


def get_rroute(address, id):
    """ get smallest reverse route by dest address and request id
    """
    global REVERSEROUTES
    arr = []
    for i in list(REVERSEROUTES):
        if int(i["requestId"]) == int(id) and int(i["source"] == address):
            arr.append(i)
    write_log("# get route: "+str(arr)+" with id: " +
              str(id) + ", source: "+str(address))
    obj = None
    for o in arr:
        if obj == None:
            obj = o
        elif obj["metic"] < o["metric"]:
            obj = o
    write_log("# route: "+str(obj))
    return obj


def handle_reply(reply: Rrep) -> bool:
    """handles incoming route reply
    Args:
        reply ([Rrep]): instance of Rrep Package
    """
    global ADDRESS
    global REVERSEROUTES
    if(reply.hopAddress != int(ADDRESS)):
        write_log("# ignore route reply")
        return False
    write_log("* reply:\t\t"+str(reply.toDict()))
    r = reply.toDict()
    write_log("* reply addr:\t\t"+str(reply.destAddress) +
              " this addr:\t"+str(ADDRESS))
    # message to frontend
    c = open_json("message-obj.json")
    c["name"] = "system-message"
    c["message"] = "got route reply to: " + \
        str(reply.originAddress) + " for: " + str(reply.destAddress)
    send_out(json.dumps(c))
    # further process, case 1: reply address is equal own address
    if int(reply.destAddress) == int(ADDRESS):
        write_log("# reply is addressed to this moudle: "+str(ADDRESS))
        route = create_route_obj(reply.originAddress, reply.prevHopAddress,
                                 "", reply.hopCount, reply.destSequence, is_route_valid(reply))
        add_route(route)
        msg = find_message(reply)

        write_log("# message found for route reply: "+str(msg.toDict()))
        execute_message(msg, route)
    # case 2: reply is dedicated to you, but to hop reply to next node
    elif int(reply.destAddress) != int(ADDRESS):
        write_log("# reply isn't for my address "+str(ADDRESS) +
                  ", scanning active route requests...")
        write_log("# all r_routes: "+str(REVERSEROUTES))
        rroute = get_rroute(reply.destAddress, reply.requestId)
        write_log("# reverse route: "+str(rroute))
        route = create_route_obj(reply.originAddress, reply.prevHopAddress,
                                 rroute["prevHop"], reply.hopCount+1, reply.originSequence, True)
        add_route(route)
        reply.hopAddress = rroute["prevHop"]
        reply.prevHopAddress = int(ADDRESS)
        reply.hopCount += 1
        send(SERIAL, encodeBase64(reply.toIntArray()), "FFFFF")
    return True


def handle_message(msg: Msg):
    write_log("# handle msg")
    global ADDRESS
    if(msg.hopAddress != int(ADDRESS)):
        # ignore messages which aren't for own address
        return False
    else:
        ack = Ack(msg.prevHopAddress, int(ADDRESS))
        send(SERIAL, encodeBase64(ack.toIntArray()), "FFFFF")
        ACTIVE_REQUESTS["msg"].append(msg)
        check_messages()

        return True
    # send ack
    # get route


def handle_client_messages(request, serial):
    global ADDRESS
    global PORT
    global BAUD

    if "name" in request:
        name = request["name"]
        if name == "init":
            write_log("# open-session")
            # current_session = session(str(uuid.uuid1()))
            # write_log(json.dumps(vars(current_session)))
            init = open_json("init.json")
            init["address"] = int(ADDRESS)
            init["port"] = PORT
            init["baud"] = BAUD
            send_out(
                json.dumps(init))
        elif name == "client-message":
            client_msg(serial, request)
            # send(serial, request["message"], "FFFFF", request["destination"])

    else:
        write_log("# key error:             .....")
        write_log("# name not found in dict .....")
        write_log("# ...................... .....")


def find_route(routeDestination):
    write_log("# check if route to "+str(routeDestination)+" exists")
    global ROUTES
    for route in ROUTES:
        if int(route["destination"]) == int(routeDestination):
            write_log("# route exists...")
            return route
    return None

# --- --------------------------------------------------------------------------


def decoding(message):
    print("# decode base64 string")
    _hex = Packets.base64_to_hex(message)
    print("= "+str(_hex))
    _bin = Packets.hex_to_binary_bits(Packets, _hex)
    return _bin


def client_msg(serial, request, count=0):
    global ADDRESS
    global ACTIVE_REQUESTS
    global SEQ_NUM
    global ROUTES
    dest = int(request["destination"])
    
    route = find_route(int(request["destination"]))
    write_log("# client message route: "+str(route))
    write_log("# routes: "+str(ROUTES))
    if route != None:
        write_log("# existing route")
        write_log("# route: "+str(route))
       
        msg = Msg(int(route["nextHop"]),int(ADDRESS),int(request["destination"]),SEQ_NUM,get_request_id(),request["message"].encode("ascii"))
        msg.viewType = "default"
        write_log("# msg: "+str(msg.toDict()))
        ACTIVE_REQUESTS["msg"].append(msg)
        write_log("# active messages: "+str(ACTIVE_REQUESTS["msg"]))
        # wait random between (0.01, 0.05) sec
        sleep(random.randint(10,50)/1000)
        check_messages()
        # send to route
    else:
        SEQ_NUM = get_sequence_number()
        msg = init_msg_from_json(
            request["destination"], request["message"], SEQ_NUM)
        write_log("message: "+str(msg.toDict()))
        send_route_request(serial, msg.messageId,
                           msg.destAddress, 0, int(ADDRESS), SEQ_NUM)
        # send route request to from


def init_msg_from_json(destination, text, seq):
    #write_log("init msg: "+ str(destination))
    dest = int(destination)
    id = get_request_id()
    msg = Msg(255, int(ADDRESS), dest, seq, id, text.encode("ascii"))
    ACTIVE_REQUESTS["msg"].append(msg)
    return msg


def send_route_request(serial, id, destination, count, origin, seq):
    global ACTIVE_REQUESTS

    r = Rreq(255, int(ADDRESS), id,
             int(destination), 0, count, origin, seq)
    ACTIVE_REQUESTS["rreq"].append(r)
    send(serial, r.toBase64(), "FFFFF")
    c = open_json("message-obj.json")
    c["name"] = "system-message"
    c["message"] = "route request made to address: " + \
        str(destination) + " | origin: "+str(origin)
    send_out(json.dumps(c))


def ignore_Rreq(rreq: Rreq) -> bool:
    global ACTIVE_REQUESTS
    for obj in list(ACTIVE_REQUESTS["rreq"]):
        if rreq.requestId == obj.requestId and rreq.originAddress == obj.originAddress:
            return True
    return False


def get_path_to_objects():
    return str(os.path.realpath(__file__)).replace(
        "service.py", "") + "obj/"


def open_json(obj_name):
    """loads json object model
    :param path: path to json model
    :type path: str
    :rtype: dict
    """
    try:
        _path = get_path_to_objects() + obj_name

        # write_log("path -> "+_path)
        f = open(_path,)
        data = json.load(f)
        f.close()
        return data
    except:
        return None


def main():

    try:
        serve()
    except KeyboardInterrupt:
        write_log("# Shutdown requested by console key interrupt")
    except Exception:
        write_log("# programm stopped with exception ...")
        traceback.print_exc(file=os.path.join(
            os.path.dirname(__file__), 'log/service.log'))
    sys.exit(0)


if __name__ == "__main__":
    main()
