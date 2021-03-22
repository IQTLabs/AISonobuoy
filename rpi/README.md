The following are the hardware and software requirements and installation instructions for the Raspberry Pi 4 buoy version.

# Hardware Requirements
TODO

# Hardware configuration installation
TODO

# Initial installation
1. Install Raspbian (buster)
2. TODO

# Installing crontab jobs
```
sudo crontab -e
```

Add the following to the end of the file:
```
*/5 * * * * /scripts/system_health.sh
1 */12 * * * /scripts/s3_prep.sh
```
