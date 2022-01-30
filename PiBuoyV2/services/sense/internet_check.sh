#!/bin/bash

wget -q --spider http://github.com

if [ $? -eq 0 ]; then
    echo "Online"
else
    echo "Offline"
fi
