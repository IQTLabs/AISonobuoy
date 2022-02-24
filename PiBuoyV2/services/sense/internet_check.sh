#!/bin/bash

if timeout 5 wget -q --spider http://github.com; then
    echo "Online"
else
    echo "Offline"
fi
