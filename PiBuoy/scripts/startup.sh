#!/bin/bash
mount /dev/sda1 /flash
./gps.sh
stty -F /dev/serial0 speed 38400
stty -F /dev/ttyUSB1 speed 9600
gpsd -n /dev/ttyUSB1 /dev/serial0 -F /var/run/gpsd.sock
pindrop --daemon --conf=/home/pi/pindrop.conf
python3 gpsc.py
