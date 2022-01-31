#!/bin/bash

/usr/bin/amixer sset ADC 40db
hostname=$(HOSTNAME)
mkdir -p /flash/telemetry/hydrophone
while true; do
        timestamp=$(date +%s%3N)
        arecord -q -D sysdefault -r 44100 -d 600 -f S16 -t wav -V mono /flash/telemetry/hydrophone/$hostname-$timestamp-hydrophone.wav
        sleep 10
done
