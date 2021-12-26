#!/usr/bin/python3.8
import serial
import time
import keyboard

#_serial = None
ADDRESS = None
SENDBYTE = 0


def reader(ser):

    s = ser.readline()
    de = s.decode("ascii")
    if "\r\n" in de:
        print("= receive:\t" + de.replace("\r\n", ""))
    else:
        print("= receive:\t" + s.decode("ascii"))
    return s


def send(_serial, message, dest):
    print("# -- send:\t" + message)
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

    # setRX(serial)
    while True:
        #text = input("send: ")
        #send(serial, text, "FFFF")
        if(serial.in_waiting > 0):
            message = reader(serial)
            handle(serial, message, SENDBYTE)
            # print("# -+ byte:\t"+str(getByte()))
        elif keyboard.is_pressed('#'):
            text = input("$ -[send]:\t")
            send(serial, text, "FFFFF")
        elif keyboard.is_pressed('q'):
            break
        # if text=="exit":
            # break
    print("serial close...")
    serial.close()
    exit(1)


def setByte(number):
    global SENDBYTE
    SENDBYTE = int(number)


def getByte():
    return SENDBYTE


def handle(serial, message, byte):
    try:
        m = message.decode("ascii").replace("\r\n", "")

        if "AT+ADDR=" in m or "AT+CFG=" in m or "AT+RX" == m or m == "AT":
            send(serial, "AT,OK", "111")
        if "AT+DEST=" in m:
            send(serial, "AT,OK", "111")
        elif "AT+SEND=" in m:
            print("# -- byte:\t"+m.split("=")[1])
            setByte(m.split("=")[1])

            send(serial, "AT,OK", "111")
        else:
            if len(m) == byte:
                print("# SEND OK")
                send(serial, "AT,SENDED", "111")

    except:
        print("decode message error")


def proceedMsg(serial, message):
    try:
        print("# --message:\t"+str(message))
    except:
        print("ERROR")


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

    sender(serial)
