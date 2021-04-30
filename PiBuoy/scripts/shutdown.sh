#!/bin/bash
date >> /var/log/shutdown.log
sync
sync
sync
/usr/sbin/poweroff
