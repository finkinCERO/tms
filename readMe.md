# Start GUI
* serial port is connected on `rfcomm0`
* you have super user permissions
```bash
$: sudo ./start.bash
```
# test with socat
```bash
$: sudo socat -v -d -d PTY,link=/dev/ttyAMA0 PTY,link=/dev/ttyS0
$: sudo chown -c $USER /dev/ttyAMA0 && sudo chown -c $USER /dev/ttyS0
# Run proof of conecpt test
$: sudo /srv/bin/test.py
# press # to send
```

# to do

## frontend
* permit input address `123a`: string + number
* render send message to after service response

## backend
* client messages
    - check if route exists (x)
    - find route if not exists
    - send routerequest to broadcast
    - handle route reply
    - handle route request from serial
    - send message
    - handle ack
    - handle route error
* build 0b format headers + data instead of b'00010101..'
