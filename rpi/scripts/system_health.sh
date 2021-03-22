#!/bin/bash

timestamp=$(date +%s%3N)
hostname=$(hostname)
output_dir=/telemetry/system/"$hostname-$timestamp"
mkdir -p "$output_dir"

timeout 5 df > "$output_dir"/df.txt
timeout 5 ifconfig -a > "$output_dir"/ifconfig.txt
timeout 5 vcgencmd measure_temp > "$output_dir"/temp.txt
timeout 5 vcgencmd measure_volts > "$output_dir"/volts.txt
timeout 5 uptime > "$output_dir"/uptime.txt
timeout 5 free > "$output_dir"/mem.txt
timeout 10 raspinfo > "$output_dir"/raspinfo.txt
