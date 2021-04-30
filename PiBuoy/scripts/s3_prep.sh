#!/bin/bash

timestamp=$(date +%s%3N)
mkdir -p /s3
XZ_OPT="-9" tar --remove-files --sort='name' -cJf /s3/system-"$timestamp".tar.xz -C /telemetry/system .
XZ_OPT="-9" tar --remove-files --sort='name' -cJf /s3/sensors-"$timestamp".tar.xz -C /telemetry/sensors .
for file in /s3/*
do
  /usr/local/bin/aws s3 cp $file s3://biggerboatwest/compressed/
  rm $file
done
