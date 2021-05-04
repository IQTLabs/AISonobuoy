#!/bin/bash
mount /dev/sda1 /flash
./gps.sh
stty -F /dev/serial0 speed 38400
stty -F /dev/ttyUSB1 speed 9600
gpsd -n /dev/ttyUSB1 -F /var/run/gpsd.sock
# TODO - both of these are foreground processes
pindrop --daemon --conf=/scripts/pindrop.conf
python3 serial_ais.py
