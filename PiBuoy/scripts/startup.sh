#!/bin/bash
mount /dev/sda1 /flash
stty -F /dev/serial0 speed 38400
stty -F /dev/ttyUSB1 speed 9600
gpsd -n /dev/ttyUSB1 /dev/serial0 -F /var/run/gpsd.sock
