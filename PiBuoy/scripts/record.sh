#!/bin/bash

COUNTER=0
while true; do
  arecord -q -D sysdefault -r 44100 -d 600 -f S16 -t wav -V mono hydrophone$COUNTER.wav
  sleep 10
  let COUNTER=COUNTER+1
done
