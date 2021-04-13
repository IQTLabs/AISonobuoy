#!/bin/bash
# enable gps
atcom --port /dev/ttyUSB2 AT\$GPSRST
sleep 2
atcom --port /dev/ttyUSB2 AT\$GPSACP
sleep 2
atcom --port /dev/ttyUSB2 AT\$GPSNMUN=2,1,1,1,1,1,1
sleep 2
atcom --port /dev/ttyUSB2 AT\$GPSP=1
