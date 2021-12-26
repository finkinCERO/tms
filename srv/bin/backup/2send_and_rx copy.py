#!/usr/bin/python3.8
import serial
import time
#import RPi.GPIO as GPIO


_serial = None


def reader(ser):

    s = ser.readline()
    print(s)
    print("returning line...")
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
    print("sending..")
    for i in range(0, 10):
        send(serial, "davis", "FFFF")
        print(str(i)+". send")
        time.sleep(1)
    setRX(serial)
    while True:
        if(serial.in_waiting > 0):
            reader(serial)
    print("serial close...")
    serial.close()


def sendIn(message):
    send(serial, "davis", "FFFF")

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
        return False
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
