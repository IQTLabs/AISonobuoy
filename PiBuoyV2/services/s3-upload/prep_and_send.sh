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

do_tar () {
    local tarfile=$1
    local tardir=$2
    local tarflags=$3
    # find files to tar and remove, that don't begin with "."
    tarfiles=$(cd $tardir && find . -type f -regex '.+\/[^\.].+$' -print)
    if [[ "$tarfiles" != "" ]] ; then
        XZ_OPT="-9" $(cd $tardir && tar --remove_files --sort='name' $tarflags -cf $tarfile ${tarfiles})
    fi
}

# wait an hour between runs
sleep 3600

hostname=$HOSTNAME
timestamp=$(date +%s%3N)
mkdir -p /flash/s3

do_tar /flash/s3/system-"$hostname"-"$timestamp".tar.xz /flash/telemetry/system -J
ship_data system

do_tar /flash/s3/power-"$hostname"-"$timestamp".tar.xz /flash/telemetry/power -J
ship_data power

do_tar /flash/s3/sensors-"$hostname"-"$timestamp".tar.xz /flash/telemetry/sensors -J
ship_data sensors

do_tar /flash/s3/ais-"$hostname"-"$timestamp".tar.xz /flash/telemetry/ais -J
ship_data ais

do_tar /flash/s3/hydrophone-"$hostname"-"$timestamp".tar /flash/telemetry/hydrophone ""
ship_data hydrophone
