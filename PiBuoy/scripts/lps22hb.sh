#!/bin/bash

timestamp=$(date +%s%3N)
hostname=$(hostname)
output_dir=/telemetry/sensors/pressure/"$hostname-$timestamp"
mkdir -p "$output_dir"

timeout 10 python3 /scripts/LPS22HB.py > "$output_dir"/lps22hb.json
