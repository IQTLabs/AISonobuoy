#!/bin/bash
# enable gps
if atcom --port /dev/ttyUSB2 AT\$GPSRST | grep -q 'ERROR'; then
  exit 1
fi
sleep 2
if atcom --port /dev/ttyUSB2 AT\$GPSACP | grep -q 'ERROR'; then
  exit 1
fi
sleep 2
if atcom --port /dev/ttyUSB2 AT\$GPSNMUN=2,1,1,1,1,1,1 | grep -q 'ERROR'; then
  exit 1
fi
sleep 2
if atcom --port /dev/ttyUSB2 AT\$GPSP=1 | grep -q 'ERROR'; then
  exit 1
fi
exit 0
