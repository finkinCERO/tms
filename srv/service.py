#!/usr/bin/python3.8
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
from bin.utils import create_reply_from_binary, parse_packet, encodeBase64, decodeBase64, write_log
from bin.packets.rreq import Rreq
import time
from bin.packets.rrep import Rrep
from bin.packets.msg import Msg
from bin.packets.rerr import Rerr
from bin.packets.ack import Ack
from bin.packets.packets import Packets
user = None
CONFIG = "433000000,5,6,12,4,1,0,0,0,0,3000,8,8"
ADDRESS = "111"
SERIAL = None
BAUD = 115200
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
    write_log("# [sending std out]:\t\t\t\t"+str(msg))
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
    route = get_route_by(address, "destination")
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
    if route!=None:
        if route["metric"] == obj["metric"] and route["nextHop"] == obj["nextHop"]:
            return False
    ROUTES.append(obj)
    response = open_json("table-wrapper.json")
    response["data"] = ROUTES
    send_out(json.dumps(response))
    write_log("# route added: "+str(obj))

    return True


def add_reverse_route(obj):
    global REVERSEROUTES
    REVERSEROUTES.append(obj)
    response = open_json("table-wrapper.json")
    response["name"] = "reverse-rounting-table"
    response["data"] = REVERSEROUTES
    send_out(json.dumps(response))
    # write_log("# reverse route added")
    return True


def send(serial, message, dest):
    m = "AT+DEST=" + dest + "\r\n"

    serial.write(m.encode())
    sleep(0.1)
    if verify_status(serial):
        print("# length\t\t->\t"+str(len(message)))
        sendMode = "AT+SEND="+str(len(message))+"\r\n"
        write_log("# [set send mode]:\t"+sendMode +
                  "# [message]\t\t->\t"+str(message))

        serial.write(sendMode.encode())
        if(verify_status(serial)):
            print("* sending...")
            m = message.decode("ascii") + "\r\n"
            serial.write(m.encode())
            verify_status(serial)
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
        if(verify_status(SERIAL) and SERIAL.in_waiting > 0):
            reader(SERIAL)


def reader(ser):
    s = ser.readline()
    # print(s)
    write_log("# read message: "+str(s))
    # send message trought websocket...

    return s.replace(b"\r\n", b"")


def send_msg_object(msg: Msg, ack: bool = False):
    if msg != b"":
        obj = open_json("message-obj.json")
        obj["message"] = msg.text.decode("ascii")
        obj["ack"] = ack
        obj["id"] = msg.messageId
        send_out(json.dumps(obj))


def config(serial, address, _config):
    # set address
    try:
        ADDRESS = address
        addr = "AT+ADDR="+address+"\r\n"
        serial.write(addr.encode())
        write_log("# adress setted to\t\t->\t"+addr)

        time.sleep(0.1)
        # config
        if(verify_status(serial)):
            CONFIG = _config
            c = "AT+CFG="+_config+"\r\n"
            serial.write(c.encode())
            write_log("# set config\t\t\t->\t"+c)
        return True
    except:
        write_log("# config failed")
        return False


def verify_status(serial):
    time.sleep(0.05)
    status = reader(serial)
    print("# verify status of module:\t"+status.decode("ascii"))
    if(status == b'AT,OK\r\n' or status == b'AT,OK\n'):
        write_log("# all fine:\t AT OK")
        return True
    elif(status == b'AT,OKERR:CPU_BUSY\r\n'):
        write_log("# resetting module")
        _serial = reset(BAUD, PORT)
        config(_serial, ADDRESS, CONFIG)
    elif(status == b'AT,SENDED\r\n'):
        write_log("# sended")
        return True
    elif(status == b'AT,SENDING\r\n'):
        write_log("# sending...")
    elif (status == b'\r\n' or status == ''):
        write_log("# empty read, verifying")
        return True
    else:
        write_log("#! not implemted device mode")
        return True


def reset(baud, port):
    write_log("# initalizing module\tport: "+port+"\tbaud:"+str(baud))
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
        write_log("# module initialized \r# baud\t" +
                  str(BAUD)+"\r# port\t"+_serial.name)
        SERIAL = _serial
        return _serial
    except:
        _error = open_json("error.json")
        _error["message"] = "Error occured during initialisation, please check port permissions of host, port name or if valid baudrate is setted"
        send_out(json.dumps(_error))
        return None


""" def get_my_route():
    myRoute = openJson("routing-table.json")
    myRoute["destination"] = ADDRESS
    myRoute["nextHop"] = ADDRESS
    myRoute["precursors"] = ""
    myRoute["metric"] = 0
    myRoute["sequenceNumber"] = 0
    myRoute["isValid"] = True
    return myRoute
 """


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
    r_route = open_json("routing-table.json")
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
                    config(_SERIAL, request["address"], request["config"])
                    send_out(json.dumps(open_json("set-config.json")))
                    _switch = True
                    clear_routes()
                    add_route(create_route_obj(
                        ADDRESS, ADDRESS, "", 0, 0, True))
                    #send(SER, "init", "FFFFF")
                    sleep(0.1)
                    set_rx(_SERIAL)
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
                    decoding_process(msg)
            elif (LAST_CHECK - time.time()*1000.0) > 4999:
                check_messages()

        else:
            sleep(0.1)
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
    write_log("# handle route request:\t\t"+rreq.toDict())
    from_addr = rreq.originAddress
    if from_addr == ADDRESS:
        return False
    prev_hop = rreq.prevHopAddress
    id = rreq.requestId
    dest_addr = rreq.destAddress
    arr = get_by_value("originAddress", from_addr, ACTIVE_REQUESTS["rrep"])
    arr = get_by_value("requestId", id, arr)
    arr = get_by_value("destinationAddress", dest_addr, arr)
    print("# rreq arr: "+arr)
    try:
        arr[0]
        return False
    except IndexError:
        write_log("# no request exists")
        route = get_route(from_addr)
        destRoute = get_route(dest_addr)
        if from_addr == prev_hop and route == None:
            route = create_route_obj(
                from_addr, from_addr, from_addr, 1, rreq.originSequence, True)
            add_route(route)
        if destRoute != None:
            rrep = Rrep(rreq.hopAddress, int(ADDRESS), rreq.requestId,
                        rreq.destAddress, rreq.destSequence, 0 + int(destRoute["metric"]), ADDRESS)
            rrep_b64 = encodeBase64(rrep.toIntArray())
            send(SERIAL, rrep_b64, "FFFFF")
            obj = open_json("message-obj.json")
            obj["message"] = "# known route asked: " + \
                route["destination"]+", next hop: " + rrep.hopAddress
            send_out(json.dumps(obj))
        else:
            last = rreq.prevHopAddress
            rreq.prevHopAddress = ADDRESS
            rreq.hopCount += 1
            r_route = create_reverse_route_obj(
                rreq.destAddress, rreq.originAddress, rreq.requestId, rreq.hopCount, last)
            add_reverse_route(r_route)
            send(SERIAL, encodeBase64(rreq.toIntArray()), "FFFFF")
            write_log("# not known route")
        # ACTIVE_REQUESTS["rrep"].append(rreq)
        # check if route to origin exsists -> no: add route to routin table
        # check if dest route is own address -> yes: send route reply
        #


def decoding_process(msg):
    # write_log("")
    write_log("# decode base64 string: " + msg.decode("ascii"))
    rType = msg.decode("ascii")[:4].encode("ascii")
    write_log("# type: "+str(rType))
    _hex = Packets.base64_to_hex(msg)
    write_log("# hex:\t\t" + _hex)
    _bin = Packets.hex_to_binary_bits(Packets, _hex)
    write_log(_bin)
    int_arr = decodeBase64(rType)
    write_log(str(int_arr))
    request_type = int(Packets.int_to_bits(int_arr[0], 8)[0:4], base=2)
    request_flags = int(Packets.int_to_bits(int_arr[0], 8)[4:8], base=2)

    write_log("*  request type:\t" + str(request_type))
    write_log("* request flags:\t" + str(request_flags))

    write_log(str(int_arr))
    if request_type == 0:
        req = parse_packet(decodeBase64(msg))
        handle_route_request(req)
        # check if route exists
        # if exists return route reply
        write_log("# route request detected")

    elif request_type == 1:
        int_arr = decodeBase64(msg)
        write_log("# route reply detected")
        handle_reply(parse_packet(int_arr))
        # check route reply
    elif request_type == 2:
        write_log("# route error detected")
        int_arr = decodeBase64(msg)
    elif request_type == 3:
        int_arr = decodeBase64(msg[:8])
        handle_message(parse_packet(int_arr, msg[8:]))
        write_log("# message detected")
    elif request_type == 4:
        int_arr = decodeBase64(msg)
        m = ACTIVE_REQUESTS["msg"][0]
        send_out(json.dumps(m.toDict()))
        pop_message()
        write_log("# ack detected")
        # find message and pass to frontend
        # delete message from active message

    write_log("#  decoding msg:\t"+str(msg))
    write_log("# - decoded msg:\t"+str(int_arr))


def is_route_valid(reply: Rrep) -> bool:
    global ACTIVE_REQUESTS
    active_route_req = ACTIVE_REQUESTS["rreq"]
    return True

LAST_CHECK = time.time()*1000.0

def check_messages():
    global ACTIVE_REQUESTS
    msgs = ACTIVE_REQUESTS["msg"]
    # write_log()
    try:
        if msgs[0] != None:
            write_log("# inwaiting message")
            m = msgs[0]
            if m.count < 3 and (m.timestamp - time.time()*1000.0) > 2999:
                m.timestamp = time.time()*1000.0
                m.count += 1
                execute_message(m, find_route(m.destination))
                return True
            elif m.count >= 3:
                obj = open_json("error.json")
                obj["message"] = "message to " + \
                    m.destinationAddress + " failed. Message: "+m.text
                send_out(json.dumps(obj))
                ACTIVE_REQUESTS["msg"].pop[0]
                return False
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
    b64 = encodeBase64(int_arr)
    b64 += msg.text
    write_log("# message:\t\t"+str(b64))
    send(SERIAL, b64, "FFFFF")


def get_rroute(address, id):
    """ get smallest reverse route by dest address and request id
    """
    global REVERSEROUTES
    arr = []
    for i in REVERSEROUTES:
        if i["requestId"] == id and i["destination"] == address:
            arr.append(i)
    obj = None
    for o in arr:
        if obj == None:
            obj = o
        elif obj["metic"] < o["metric"]:
            obj = o
    return obj


def handle_reply(reply: Rrep) -> bool:
    """handles incoming route reply
    Args:
        reply ([Rrep]): instance of Rrep Package
    """
    global ADDRESS
    if(reply.hopAddress != int(ADDRESS)):
        write_log("# reply not for my address")
        return False
    write_log("* reply:\t\t"+str(reply.toDict()))
    r = reply.toDict()
    write_log("* reply addr:\t\t"+str(reply.destAddress) +
              " this addr:\t"+ADDRESS)
    c = open_json("message-obj.json")
    c["name"] = "system-message"
    c["message"] = "got route reply to: " + \
        str(reply.originAddress) + " for: " + str(reply.destAddress)
    send_out(json.dumps(c))
    if int(reply.destAddress) == int(ADDRESS):
        write_log("# reply is addressed to this moudle: "+str(ADDRESS))
        route = create_route_obj(reply.originAddress, reply.hopAddress,
                                 reply.prevHopAddress, reply.hopCount, reply.destSequence, is_route_valid(reply))
        add_route(route)
        msg = find_message(reply)

        write_log("# message found for route reply: "+str(msg.toDict()))
        execute_message(msg, route)

    elif int(reply.destAddress) != int(ADDRESS):
        write_log("# reply isn't for my address "+str(ADDRESS) +
                  ", scanning active route requests...")
        rroute = get_rroute(reply.destAddress, reply.requestId)
        route = create_route_obj(reply.originAddress, reply.prevHopAddress,
                                 rroute["prevHop"], reply.hopCount+1, reply.originSequence, True)
        add_route(route)
        reply.hopAddress = rroute["prevHop"]
        reply.prevHopAddress = ADDRESS
        reply.hopCount += 1
        send(SERIAL, encodeBase64(reply.toIntArray()), "FFFFF")
    return True


def handle_message():
    write_log("# handle msg")


def handle_client_messages(request, serial):
    global ADDRESS
    global PORT
    global BAUD

    if "name" in request:
        name = request["name"]
        if name == "init":
            write_log("# open-session")
            #current_session = session(str(uuid.uuid1()))
            # write_log(json.dumps(vars(current_session)))
            init = open_json("init.json")
            init["address"] = ADDRESS
            init["port"] = PORT
            init["baud"] = BAUD
            send_out(
                json.dumps(init))
        elif name == "client-message":
            client_msg(serial, request)
            #send(serial, request["message"], "FFFFF", request["destination"])

    else:
        write_log("# key error:             .....")
        write_log("# name not found in dict .....")
        write_log("# ...................... .....")


def find_route(routeDestination):
    write_log("# check if route to "+str(routeDestination)+" exists")
    global ROUTES
    for route in ROUTES:
        if route["destination"] == routeDestination:
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
    dest = int(request["destination"])
    seq = get_sequence_number()
    route = find_route(request["destination"])
    if route != None:
        write_log("existing route")
        # send to route
    else:
        send_route_request(serial, request, seq)
        # send route request to from


def create_msg_from_json(request, id, seq):
    dest = int(request["destination"])
    m = request["message"]
    msg = Msg(255, int(ADDRESS), dest, seq, id, m.encode("ascii"))
    return msg


def send_route_request(serial, request, seq):
    global ACTIVE_REQUESTS
    id = get_request_id()
    msg = create_msg_from_json(request, id, seq)

    r = Rreq(255, int(ADDRESS), id,
             int(request["destination"]), get_dest_sequence_number(), 0, int(ADDRESS), seq)
    ACTIVE_REQUESTS["rreq"].append(r)
    ACTIVE_REQUESTS["msg"].append(msg)
    send(serial, r.toBase64(), "FFFFF")
    c = open_json("message-obj.json")
    c["name"] = "system-message"
    c["message"] = "route request made to address: "+request["destination"]
    obj = r.getInfos()
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
