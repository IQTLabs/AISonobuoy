#!/bin/bash
date >> /var/log/shutdown.log
/usr/bin/env bash /scripts/s3_prep.sh
sync
sync
sync
/usr/sbin/poweroff
