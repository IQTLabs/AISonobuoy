#!/bin/bash
set -e

while true
do
  flacdir=/flash/telemetry/hydrophone
  /usr/bin/amixer sset ADC 40db
  hostname=$HOSTNAME
  mkdir -p $flacdir
  timestamp=$(date +%s)
  flacout=$hostname-$timestamp-hydrophone.flac
  arecord -q -D sysdefault -r 44100 -d 600 -f S16 -V mono - | ffmpeg -i - -y -ac 1 -ar 16000 -sample_fmt s16 "$flacdir/.$flacout"
  tmpflacs=$(find $flacdir -type f -name ".*.flac")
  for tmpflac in $tmpflacs ; do
      dname=$(dirname "$tmpflac")
      bname=$(basename "$tmpflac")
      outflac=$dname/${bname:1}
      mv "$tmpflac" "$outflac"
  done
done
