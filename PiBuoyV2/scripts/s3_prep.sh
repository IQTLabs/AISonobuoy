#!/bin/bash

timestamp=$(date +%s%3N)
mkdir -p /flash/s3
XZ_OPT="-9" tar --remove-files --sort='name' -cJf /flash/s3/system-"$timestamp".tar.xz -C /flash/telemetry/system .
mkdir -p /flash/telemetry/system
XZ_OPT="-9" tar --remove-files --sort='name' -cJf /flash/s3/sensors-"$timestamp".tar.xz -C /flash/telemetry/sensors .
mkdir -p /flash/telemetry/sensors
XZ_OPT="-9" tar --remove-files --sort='name' -cJf /flash/s3/ais-"$timestamp".tar.xz -C /flash/telemetry/ais .
mkdir -p /flash/telemetry/ais
for file in /flash/telemetry/hydrophone/*
do
  ffmpeg -y -i $file -ac 1 -ar 16000 -sample_fmt s16 $file-scaled.wav
  rm $file
done
XZ_OPT="-9" tar --remove-files --sort='name' -cJf /flash/s3/hydrophone-"$timestamp".tar.xz -C /flash/telemetry/hydrophone .
mkdir -p /flash/telemetry/hydrophone

ship_data () {
  for file in /flash/s3/$1*
  do
    /usr/local/bin/aws s3 cp $file s3://aisonobuoywest/compressed/
    if [ $? -eq 0 ]
    then
      rm $file
    fi
  done
}

ship_data system
ship_data sensors
ship_data ais
ship_data hydrophone
