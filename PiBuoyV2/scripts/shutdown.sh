#!/bin/bash

signal=$(cat /var/run/shutdown.signal)
if [ "$signal" == "true" ]; then
  echo "done" > /var/run/shutdown.signal
  docker ps -q | xargs docker stop
  date >> /var/log/shutdown.log
  sync
  sync
  sync
  /usr/sbin/poweroff
fi
