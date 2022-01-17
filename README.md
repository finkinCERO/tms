# Start GUI
* serial port is connected on `rfcomm0`
* you have super user permissions or read/write access to `rfcomm0`

```bash
$: sudo ./start.bash
```

# test with socat

```bash
$: sudo socat -v -d -d PTY,link=/dev/ttyAMA0 PTY,link=/dev/ttyS0
$: sudo chown -c $USER /dev/ttyAMA0 && sudo chown -c $USER /dev/ttyS0
# Run proof of conecpt test
$: sudo /srv/bin/test-poc.py
# press # to send
```

# to do

## frontend

* permit input address `123a`: string + number
* render send `message to` after service response ack

## backend

* client messages
    - check if route exists (x)
    - find route if not exists 
        - init route request sended (x)
        - wait for route reply in service with timeout
    - send routerequest to broadcast (x)
    - handle route reply originator client (current)
    - send message packet

* serial messages
    - handle route request from serial
    - add successful routerequest to reverse routing table
    - handle route reply for another client
    - handle route error
    - handle ack
    - handle message packet from serial 