#!/bin/sh

echo 'true' | tee /var/run/shutdown.signal > /dev/null
