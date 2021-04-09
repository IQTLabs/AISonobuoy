#!/bin/bash

timestamp=$(date +%s%3N)
hostname=$(hostname)
output_dir=/telemetry/sensors/9axis/"$hostname-$timestamp"
mkdir -p "$output_dir"

timeout 58 python3 /scripts/ICM20948.py > "$output_dir"/icm20948.json
