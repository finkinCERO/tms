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


user = None

_serial = None


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
js_dir = os.path.join(dirname, 'bin')
running_true = 1
# TODO commandssetRX
# --- --------------------------------------------------------------------------


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
    write_log("# [sending std out] -> "+str(msg))
    # write_log(str(msg))
    stdout.write(str(msg)+'\n')
    stdout.flush()

# --- --------------------------------------------------------------------------


def send(message, dest):
    m = "AT+DEST=" + dest + "\r\n"
    if(_serial == None):
        _serial = reset()
    _serial.write(m.encode())
    if verify_status(_serial):
        print("# length -> "+str(len(message)))
        sendMode = "AT+SEND="+str(len(message))+"\r\n"
        write_log("[set send mode]: "+sendMode+" [message] -> "+str(message))

        _serial.write(sendMode.encode())
        if(verify_status(_serial)):
            print("sending...")
            m = message + "\r\n"
            _serial.write(m.encode())
            verify_status(_serial)
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
    write_log("# read message -> "+str(s))
    # send message trought websocket...

    return s


def sendMessageObj(msg):
    if msg != b"" or msg != "":
        obj = openJson("message-obj.json")
        obj["message"] = msg.decode("ascii")
        sendOut(msg)


def config(serial):
    # set address
    addr = "AT+ADDR=0114\r\n"
    serial.write(addr.encode())
    write_log("# adress setted to ->"+addr)

    time.sleep(0.1)
    # config
    if(verify_status(serial)):
        config = "AT+CFG=433000000,5,6,12,4,1,0,0,0,0,3000,8,8\r\n"

        serial.write(config.encode())
        write_log("# config setted to -> "+config)
    # set rx mode
    #time.sleep(0.1)
    #if(verify_status(serial)):
    #    setRX(serial)
    return True


def verify_status(serial):
    print("check reading")
    time.sleep(0.1)
    status = reader(serial)
    if(status == b'AT,OK\r\n' or status == b'AT,OK\n'):
        write_log("# all fine, AT OK")
        return True
    elif(status == b'AT,OKERR:CPU_BUSY\r\n'):
        write_log("# resetting...")
        _serial = reset()
        config(_serial)
    elif(status == b'AT,SENDED\r\n'):
        write_log("# sended")
        return True
    elif(status == b'AT,SENDING\r\n'):
        write_log("# sending...")
    else:
        write_log("#! not implemted device mode")
        return False
    write_log("# passing check with status -> "+status.decode("ascii"))
    return False


def reset():
    print("# resetting modul...")
    _serial = serial.Serial()
    _serial.baudrate = 115200
    #_serial.port = '/dev/rfcomm0'
    
    _serial.port = '/dev/ttyS0'
    _serial.open()
    _serial.flush()
    # config(_serial)
    return _serial


def serve(serial):
    """
    listening on std in,
    std in messages -> json string
    """

    exit_cmd = 'exit'
    # global passphrase
    wrong_message_counter = 0
    write_log("# start server")
    SER = None
    if(serial == None):
        SER = reset()
        write_log("# serial is null")
    else:
        SER = serial
    while True:
        # Websocket:
        requestRaw = stdin.readline().strip()

        if requestRaw != "":
            write_log("# incoming request -> "+requestRaw)
            request = json.loads(requestRaw)
            handleClientMessage(request, SER)
        if(verify_status(SER) and SER.in_waiting > 0):
            write_log("# message is inwaiting...")
            msg = reader(SER)
            if msg != b'':
                sendMessageObj(msg)
        # if(_serial.in_waiting > 0):
        #    write_log("# message is inwaiting...")
        #    msg = reader(_serial)
        #    sendMessageObj(msg)
        #    if msg != b'':
        #        sendMessageObj(msg)


def handleClientMessage(request, serial):
    if "name" in request:
        name = request["name"]
        if name == "init":
            write_log("# open-session")
            current_session = session(str(uuid.uuid1()))
            # write_log(json.dumps(vars(current_session)))
            sendOut(
                json.dumps(openJson("init.json")))
        elif name == "client-message":
            send(request["message"], "FFFFF")

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
        if(config(_serial)):
            setRX(_serial)
            serve(_serial)
            t0 = threading.Thread(target=serve)
            t0.start()
            t0.join()
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
    _serial = reset()
    main()
