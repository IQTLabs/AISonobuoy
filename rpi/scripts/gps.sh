#!/bin/bash
# enable gps
atcom --port /dev/ttyUSB2 AT\$GPSP=0
sleep 2
atcom --port /dev/ttyUSB2 AT\$GPSR=0
sleep 2
atcom --port /dev/ttyUSB2 AT\$GPSP=1
sleep 2
atcom --port /dev/ttyUSB2 AT\$GPSP?
sleep 2
atcom --port /dev/ttyUSB2 AT\$GPSNMUN=2,1,1,1,1,1,1
sleep 2
atcom --port /dev/ttyUSB2 AT\$GPSQOS=0,0,0,0,2,3,1
sleep 2
atcom --port /dev/ttyUSB2 AT\$GPSSAV
