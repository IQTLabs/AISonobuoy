#!/bin/bash

ship_data () {
  for file in /flash/s3/$1*
  do
    /usr/local/bin/aws s3 cp $file s3://aisonobuoy-pibuoy-v2/compressed/
    if [ $? -eq 0 ]
    then
      rm $file
    fi
  done
}

# wait an hour between runs
sleep 3600

hostname=$HOSTNAME
timestamp=$(date +%s%3N)
mkdir -p /flash/s3

XZ_OPT="-9" tar --remove-files --sort='name' -cJf /flash/s3/system-"$hostname"-"$timestamp".tar.xz -C /flash/telemetry/system .
mkdir -p /flash/telemetry/system
ship_data system

XZ_OPT="-9" tar --remove-files --sort='name' -cJf /flash/s3/power-"$hostname"-"$timestamp".tar.xz -C /flash/telemetry/power .
mkdir -p /flash/telemetry/power
ship_data power

XZ_OPT="-9" tar --remove-files --sort='name' -cJf /flash/s3/sensors-"$hostname"-"$timestamp".tar.xz -C /flash/telemetry/sensors .
mkdir -p /flash/telemetry/sensors
ship_data sensors

XZ_OPT="-9" tar --remove-files --sort='name' -cJf /flash/s3/ais-"$hostname"-"$timestamp".tar.xz -C /flash/telemetry/ais .
mkdir -p /flash/telemetry/ais
ship_data ais

for file in /flash/telemetry/hydrophone/*
do
  ffmpeg -y -i $file -ac 1 -ar 16000 -sample_fmt s16 $file-scaled.flac
  rm $file
done
tar --remove-files --sort='name' -cJf /flash/s3/hydrophone-"$hostname"-"$timestamp".tar.xz -C /flash/telemetry/hydrophone .
mkdir -p /flash/telemetry/hydrophone
ship_data hydrophone

