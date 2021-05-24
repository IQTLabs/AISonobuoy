#!/bin/bash
date >> /var/log/shutdown.log
systemctl stop ais.service
systemctl stop record.service
systemctl stop pindrop.service
/usr/bin/env bash /opt/BiggerBoat/PiBuoy/scripts/s3_prep.sh
sudo umount /flash
sync
sync
sync
/usr/sbin/poweroff
