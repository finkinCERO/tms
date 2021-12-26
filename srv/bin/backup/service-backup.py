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
from bin.packets import Packets
user = None
CONFIG = "433000000,5,6,12,4,1,0,0,0,0,3000,8,8"
ADDRESS = "0114"
_serial = None
BAUD = None
PORT = None


def saveFile(path, data):
    _path = getPathToObjects() + "obj/export/"+path
    with open(_path, 'w') as f:
        json.dump(data, f)


# --- --------------------------------------------------------------------------


class session:
    uuid = ""

    def __init__(self, uuid):
        self.uuid = uuid

# --- --------------------------------------------------------------------------


class message_object:
    name = ""
    message = ""

    def __init__(self, name, message):
        self.name = name
        self.message = message


# --- --------------------------------------------------------------------------
dirname = os.path.dirname(__file__)
log_file = os.path.join(dirname, 'log/service.log')


def write_log(msg):
    global log_file
    f = open(log_file, "a+")
    f.write(msg+'\n')
    f.flush()
    f.close()

# --- --------------------------------------------------------------------------


def sendOut(msg):
    """
    sends message trough std out, websocket daemon
    can pass to frontend connection
    (push messages without request to frontend or as a reaction to a request)

    :param msg: msg to send out
    :type path: str
    :rtype: True | None
    """
    # send string to web page
    write_log("# [sending std out]:\t"+str(msg))
    # write_log(str(msg))
    stdout.write(str(msg)+'\n')
    stdout.flush()

# --- --------------------------------------------------------------------------


def send(serial, message, dest):
    m = "AT+DEST=" + dest + "\r\n"

    serial.write(m.encode())
    if verify_status(serial):
        print("# length\t\t->\t"+str(len(message)))
        sendMode = "AT+SEND="+str(len(message))+"\r\n"
        write_log("# [set send mode]:\t"+sendMode +
                  "# [message]\t\t->\t"+str(message))

        serial.write(sendMode.encode())
        if(verify_status(serial)):
            print("* sending...")
            m = message + "\r\n"
            serial.write(m.encode())
            verify_status(serial)
            return True
        else:
            return False
    else:
        return False


def setRX(serial):
    rxMode = "AT+RX\r\n"
    serial.write(rxMode.encode())
    write_log("# set RX")
    _serial = serial
    time.sleep(0.1)

    return True


def sender():
    write_log("# sending..")

    setRX(_serial)
    while True:
        if(verify_status(_serial) and _serial.in_waiting > 0):
            reader(_serial)


def reader(ser):
    s = ser.readline()
    # print(s)
    write_log("# read message\t\t\t->\t"+str(s))
    # send message trought websocket...

    return s


def sendMessageObj(msg):
    if msg != b"":
        obj = openJson("message-obj.json")
        obj["message"] = msg.decode("ascii")
        sendOut(json.dumps(obj))


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
    print("# initalizing modul...")
    BAUD = baud
    PORT = port
    _serial = serial.Serial()
    _serial.baudrate = baud  # 115200
    #_serial.port = '/dev/rfcomm0'

    _serial.port = port  # '/dev/ttyS0'
    _serial.open()
    _serial.flush()
    # config(_serial)
    write_log("# module initialized \r# baud\t" +
              str(BAUD)+"\r# port\t"+_serial.name)
    return _serial


def serve():
    """
    listening on std in,
    std in messages -> json string
    """

    exit_cmd = 'exit'
    # global passphrase
    wrong_message_counter = 0
    write_log("# start server")
    SER = None
    _switch = False
    while True:
        # Websocket:
        requestRaw = ""
        # check if line should be readed from stdin
        if select.select([sys.stdin,],[],[],0.0)[0]:
            requestRaw = stdin.readline()
        # procceed client messages
        if requestRaw != "":
            write_log("# client request\t\t->\t"+requestRaw)
            request = json.loads(requestRaw)

            # ----------------------------------------------------
            # module settings
            if(request["name"] == "reset-module"):
                SER = reset(request["baud"], request["port"])
                sendOut(json.dumps(openJson("reset.json")))
                _switch = False
            elif(request["name"] == "set-config"):
                config(SER, request["address"], request["config"])
                sendOut(json.dumps(openJson("set-config.json")))
                _switch = True
                
                write_log("# check:\t"+str(_switch)+"\r# SERIAL:\t"+SER.name+"\r# "+str(verify_status(SER)))
                setRX(SER)
            # ----------------------------------------------------
            # client messages
            else:
                write_log("# handle client messages\t->\t"+requestRaw)
                handleClientMessage(request, SER)
        elif _switch == True:
            # write_log("# test")
            if(SER.in_waiting > 0):
                write_log("# in waiting")
                msg = reader(SER)
                if msg != b'':
                    sendMessageObj(msg)
        else:
            sleep(0.5)
            write_log("# NO ACTION")
            # SER.write("AT\r\n".encode())

        # if(_serial.in_waiting > 0):
        #    write_log("# message is inwaiting...")
        #    msg = reader(_serial)
        #    sendMessageObj(msg)
        #    if msg != b'':
        #        sendMessageObj(msg)
    write_log("# serve stop")


def handleClientMessage(request, serial):
    if "name" in request:
        name = request["name"]
        if name == "init":
            write_log("# open-session")
            current_session = session(str(uuid.uuid1()))
            # write_log(json.dumps(vars(current_session)))
            sendOut(
                json.dumps(openJson("init.json")))
        elif name == "set-config":
            write_log("# open-session")
            current_session = session(str(uuid.uuid1()))
            # write_log(json.dumps(vars(current_session)))
            sendOut(
                json.dumps(openJson("init.json")))
        elif name == "client-message":
            send(serial, request["message"], "FFFFF")

    else:
        write_log("# key error:             .....")
        write_log("# name not found in dict .....")
        write_log("# ...................... .....")


# --- --------------------------------------------------------------------------


def getPathToObjects():
    return str(os.path.realpath(__file__)).replace(
        "service.py", "") + "obj/"


def openJson(obj_name):
    """loads json object model
    :param path: path to json model
    :type path: str
    :rtype: dict
    """
    try:
        _path = getPathToObjects() + obj_name

        # write_log("path -> "+_path)
        f = open(_path,)
        data = json.load(f)
        f.close()
        return data
    except:
        return None


def check_passphrase(passphrase):
    check = "satis001"
    if passphrase != check:
        write_log("# ERROR => wrong passphrase detected: " + passphrase + check)
        exit(-1)

# --- --------------------------------------------------------------------------


def main():

    try:

        # write_log("# serial name -> "+serial.name)

        serve()
        # write_log("# starting THREAD 1 started")
        # t1 = threading.Thread(target=sender)
        # t1.start()
        # t0 = threading.Thread(target=receive)

        # write_log("# starting THREAD 0 started")
        # t0.start()
        # t0.join()
        # t1.join()
        write_log("# programm stopped ...")
    except KeyboardInterrupt:
        write_log("# programm stopped with exception ...")
        write_log("# Shutdown requested via console")
    except Exception:
        write_log("# programm stopped with exception ...")
        traceback.print_exc(file=log_file)
    sys.exit(0)


if __name__ == "__main__":
    #_serial = reset()
    main()
