#!/bin/bash

if wget -q --spider http://github.com; then
    echo "Online"
else
    echo "Offline"
fi
