#!/bin/bash

DURATION=$1

if [[ "$DURATION" == "" ]] ; then
	echo need duration
	exit 1
fi

DEV=/dev/ttyS0
stty -F $DEV 9600 time 2 min 100 -icrnl -imaxbel -opost -onlcr -isig -icanon -echo || exit 1
SCMD="{\"command\": \"snooze\", \"duration\": $DURATION}"

(read -n96 -t5 RESP < $DEV; echo $RESP)&
read -p "" -t 1
echo $SCMD
printf "$SCMD\r" > $DEV || exit 1
wait
echo $RESP
RES=$(echo $RESP | grep snooze)
if [[ "$RES" != "" ]] ; then
	exit 1
fi
sudo poweroff
