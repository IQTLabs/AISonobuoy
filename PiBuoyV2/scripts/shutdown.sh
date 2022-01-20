#!/bin/bash
date >> /var/log/shutdown.log
systemctl stop ais.service
systemctl stop record.service
/usr/bin/env bash /opt/AISonobuoy/PiBuoyV2/scripts/s3_prep.sh
sync
sync
sync
/usr/sbin/poweroff
