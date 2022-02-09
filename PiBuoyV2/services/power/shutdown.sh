#!/bin/sh

echo 'true' | sudo tee /var/run/shutdown.signal > /dev/null
