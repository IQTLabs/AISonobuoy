#!/bin/bash

URL=$1
FILE=$(ls /flash/telemetry/pindrop/*.json 2>&1)

if [ $? -eq 0 ];
then
    tail -n 1 $FILE > /tmp/status.json
    sed -i 's|"|\\"|g' /tmp/status.json
    sed -i 's/{/{"text": "{/' /tmp/status.json
    echo -n '"}' >> /tmp/status.json
    curl -H 'Content-Type: application/json' -d @/tmp/status.json $URL
else
    curl -H 'Content-Type: application/json' -d '{"text": "no current GPS file to read from, but am still alive"}' $URL
fi
