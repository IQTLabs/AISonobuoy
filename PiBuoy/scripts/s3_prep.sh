#!/bin/bash

timestamp=$(date +%s%3N)
mkdir -p /flash/s3
XZ_OPT="-9" tar --remove-files --sort='name' -cJf /flash/s3/system-"$timestamp".tar.xz -C /flash/telemetry/system .
XZ_OPT="-9" tar --remove-files --sort='name' -cJf /flash/s3/sensors-"$timestamp".tar.xz -C /flash/telemetry/sensors .
XZ_OPT="-9" tar --remove-files --sort='name' -cJf /flash/s3/pindrop-"$timestamp".tar.xz -C /flash/telemetry/pindrop .
XZ_OPT="-9" tar --remove-files --sort='name' -cJf /flash/s3/ais-"$timestamp".tar.xz -C /flash/telemetry/ais .
for file in /flash/telemetry/hydrophone/*
do
  ffmpeg -y -i $file -ac 1 -ar 16000 -sample_fmt s16 scaled-$file
  rm $file
done
XZ_OPT="-9" tar --remove-files --sort='name' -cJf /flash/s3/hydrophone-"$timestamp".tar.xz -C /flash/telemetry/hydrophone .
mkdir -p /flash/telemetry/system
mkdir -p /flash/telemetry/sensors
mkdir -p /flash/telemetry/pindrop
mkdir -p /flash/telemetry/ais
for file in /flash/s3/*
do
  /usr/local/bin/aws s3 cp $file s3://biggerboatwest/compressed/
  if [ $? -eq 0 ]
  then
    rm $file
  fi
done
