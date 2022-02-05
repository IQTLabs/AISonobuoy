#!/bin/bash

signal=$(cat /var/run/shutdown_signal)
if [ "$signal" == "true" ]; then
  echo "done" > /var/run/shutdown_signal
  date >> /var/log/shutdown.log
  sync
  sync
  sync
  /usr/sbin/poweroff
fi
