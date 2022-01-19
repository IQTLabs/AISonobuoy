#!/bin/bash
# do this twice, sometimes it doesn't take the first time
timeout 10 stty -F /dev/serial0 speed 38400
timeout 10 stty -F /dev/serial0 speed 38400
mkdir -p /flash/telemetry/hydrophone
amixer -D sysdefault cset name='ADC Capture Volume' 96,96
