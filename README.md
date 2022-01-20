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

## Full documentation in file TMS-DOKUMENTATION.pdf