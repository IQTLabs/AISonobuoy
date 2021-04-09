#!/bin/bash

timestamp=$(date +%s%3N)
hostname=$(hostname)
output_dir=/telemetry/sensors/temperature/"$hostname-$timestamp"
mkdir -p "$output_dir"

timeout 30 python3 /scripts/SHTC3.py > "$output_dir"/shtc3.json
