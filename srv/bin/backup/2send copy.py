#!/usr/bin/python3.8
import serial
import time
#import RPi.GPIO as GPIO


_serial = None


def reader(ser):
    if(ser==None):
        print("serial is null")
        exit(1)
    print("# reading line")
    s = ser.readline()
    print(s)
    return s


def send(_serial, message, dest):
    m = "AT+DEST=" + dest + "\r\n"
    _serial.write(m.encode())
    if check(_serial):
        print("# length -> "+str(len(message)))
        sendMode = "AT+SEND="+str(len(message))+"\r\n"
        print("# set send mode: "+sendMode+" message -> "+str(message))

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


def sender(serial):
    print("start sending process..")

    setRX(serial)
    while True:
        text = input("send: ")
        send(serial, text, "FFFFF")
        if text == "exit":
            break
    print("serial close...")
    serial.close()
    exit(1)


def sendIn(message):
    send(serial, "davis", "FFFF")


def config(serial):
    # set address
    addr = "AT+ADDR=0114\r\n"
    serial.write(addr.encode())
    print("# adress setted to ->"+addr)

    time.sleep(0.1)
    # config
    if(check(serial)):
        config = "AT+CFG=433000000,5,6,12,4,1,0,0,0,0,3000,8,8\r\n"

        serial.write(config.encode())
        print("# config setted to -> "+config)
    # set rx mode
    time.sleep(0.1)
    if(check(serial)):
        setRX(serial)
    return True


def check(serial):
    if(serial == None):
        print("serial is null")
        exit(1)
    msg = reader(serial)
    
    if(msg == b'AT,OK\r\n'):
        print("OK!")
        return True
    elif(msg == b'AT,OKERR:CPU_BUSY\r\n'):
        print("resetting...")
        reset()
    elif(msg == b'AT,SENDED\r\n'):
        return True
    elif(msg == b'AT,SENDING\r\n'):
        print("sending...")
        return False
    else:
        print("not implemted device mode: "+msg.decode("ascii"))
        return True
    return False


def reset():
    print("resetting modul...")
    _serial = serial.Serial()
    _serial.baudrate = 115200
    _serial.port = '/dev/ttyAMA0'
    _serial.open()
    _serial.flush()
    return _serial
    # GPIO.setmode(GPIO.BCM)
    #GPIO.setup(18, GPIO.OUT)
    #GPIO.output(18, GPIO.HIGH)
    # time.sleep(1)
    #GPIO.output(18, GPIO.LOW)
    # GPIO.cleanup()


if __name__ == "__main__":
    serial = reset()
    print(serial.name)
    if(config(serial)):
        print("config passed")
        sender(serial)
    else:
        print("not okay...")
