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
# TODO commands
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
    write_log("[sending std out] -> "+str(msg))

    write_log(str(msg))
    stdout.write(msg+'\n')
    stdout.flush()
    return True

# --- --------------------------------------------------------------------------


def send(message, dest):
    m = "AT+DEST=" + dest + "\r\n"
    if(_serial==None):
        _serial = reset()
    _serial.write(m.encode())
    if check(_serial):
        print("# length -> "+str(len(message)))
        sendMode = "AT+SEND="+str(len(message))+"\r\n"
        write_log("[set send mode]: "+sendMode+" [message] -> "+str(message))

        _serial.write(sendMode.encode())
        if(check(_serial)):
            print("sending...")
            m = message + "\r\n"
            _serial.write(m.encode())
            check(_serial)
            return True
        else:
            return False
    else:
        return False


def setRX(serial):
    rxMode = "AT+RX\r\n"
    print("set RX")
    serial.write(rxMode.encode())

    return True


def sender():
    print("sending..")

    setRX(_serial)
    while True:
        if(check(_serial) and _serial.in_waiting > 0):
            reader(_serial)
        text = input("# send: ")
        send(text, "FFFFF")
        if text=="exit":
            break
    print("serial close...")
    serial.close()


def reader(ser):
    s = ser.readline()
    # print(s)
    write_log("read message -> "+s)
    # send message trought websocket...
    if s != "":
        obj = json.loads(openJson("message-obj.json"))
        obj["message"] = s
        sendOut(json.dumps(obj))
    return s


def config(serial):
    # set address
    addr = "AT+ADDR=0014\r\n"
    print("setting address -> "+addr)
    serial.write(addr.encode())
    print("serial write")
    # config
    if(check(serial)):
        config = "AT+CFG=433400000,5,6,12,4,1,0,0,0,0,3000,8,8\r\n"
        print("config...")
        serial.write(config.encode())
    # set rx mode
    if(check(serial)):
        print("set rx")
        setRX(serial)
    print("config end")
    return True


def check(serial):
    print("check reading")
    s = reader(serial)
    if(s == b'AT,OK\r\n'):
        print("OK!")
        return True
    elif(s == b'AT,OKERR:CPU_BUSY\r\n'):
        print("resetting...")
        reset()
    elif(s == b'AT,SENDED\r\n'):
        return True
    elif(s == b'AT,SENDING\r\n'):
        print("sending...")
    else:
        print("not implemted device mode")
        return False
    print("passing check")
    return False


def reset():
    print("resetting modul...")
    _serial = serial.Serial()
    _serial.baudrate = 115200
    _serial.port = '/dev/rfcomm0'
    _serial.open()
    _serial.flush()
    return _serial


def receive():
    """
    listening on std in,
    std in messages -> json string
    """

    exit_cmd = 'exit'
    #global passphrase
    wrong_message_counter = 0
    while True:
        requestRaw = stdin.readline().strip()
        write_log(requestRaw)
        if requestRaw != "":
            request = json.loads(requestRaw)
            if "name" in request:
                name = request["name"]
                if name == "init":
                    write_log("open-session")
                    current_session = session(str(uuid.uuid1()))
                    write_log(json.dumps(vars(current_session)))
                    sendOut(
                        json.dumps(openJson("init.json")))
                elif name == "client-message":
                    send(request["message"], "FFFFF")

            else:
                write_log("... key error:             .....")
                write_log("... name not found in dict .....")
                write_log("... ...................... .....")
        else:
            # only seems to happen after the websocket is closed
            #            write_log("t is empty")
            break

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
        write_log("ERROR => wrong passphrase detected: " + passphrase + check)
        exit(-1)

# --- --------------------------------------------------------------------------


def main():
    
    
    try:
        write_log("programm started ...")
        t0 = threading.Thread(target=receive)
        t0.start()
        t0.join()
        #write_log("# serial name -> "+serial.name)
        if(config(serial)):
            write_log("# THREAD 1 started")
            
            t1 = threading.Thread(target=sender)
            t1.start()
            t1.join()
        write_log("programm stopped ...")
    except KeyboardInterrupt:
        write_log("programm stopped with exception ...")
        print("Shutdown requested via console")
    except Exception:
        write_log("programm stopped with exception ...")
        traceback.print_exc(file=log_file)
    sys.exit(0)


if __name__ == "__main__":
    _serial = reset()
    main()
