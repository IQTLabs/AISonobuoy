The following are the hardware and software requirements and installation instructions for the Raspberry Pi 4 buoy version.

# Hardware Requirements

TODO

# Hardware configuration installation

1. Wire sensehat

2. Solder HifiBerry header

# Initial installation

1. Install Raspberry Pi OS on the SD card for the Raspberry Pi.

2. Put the [config.txt](config/config.txt) in `/boot/config.txt`. Reboot.

3. Install required packages.
```
sudo apt-get update
sudo apt-get install curl ffmpeg tmux screen libglib2.0-dev
```

4. Install this repo.
```
sudo su -
cd /opt
git clone https://github.com/IQTLabs/AISonobuoy.git
```

5. Install required Python packages.
```
cd /opt/AISonobuoy/PiBuoyV2/scripts
sudo pip3 install -r requirements.txt
```
6. Set WLAN Country using `sudo raspi-config`.

7. Setup [dAISy HAT](https://wegmatt.com/files/dAISy%20HAT%20AIS%20Receiver%20Manual.pdf).
```
wget https://github.com/itemir/rpi_boat_utils/raw/master/uart_control/uart_control
chmod +x ./uart_control
sudo ./uart_control gpio
```

8. Install services.
```
sudo cp /opt/AISonobuoy/PiBuoyV2/config/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ais.service
sudo systemctl enable record.service
sudo systemctl enable s_hat.service
```

9. Schedule jobs in crontab.
```
sudo crontab -e
```
Add the following lines, save, and quit:
```
# every five minutes
*/5 * * * * /opt/AISonobuoy/PiBuoyV2/scripts/system_health.sh
# once an hour, one minute past the hour
1 * * * * /usr/bin/env bash /opt/AISonobuoy/PiBuoyV2/scripts/s3_prep.sh
```

10. Edit the `s3://` path in `/opt/AISonobuoy/PiBuoyV2/scripts/s3_prep.sh` to be an S3 bucket you want to push data to.

11. Add [AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) using `aws configure`.

12. Set hostname using `sudo raspi-config`.

13. Restart.
```
sudo reboot
```

# Verify components are working
1. Check logs in `/var/log/syslog`, `/var/log/messages`.

2. Check `dmesg` for errors.

3. Check for data in `/flash/telemetry`.

4. Check serial connection for AIS.
```
sudo screen /dev/serial0 38400
<press ESC> (you should see a menu)
<press ESC>
<ctrl>+a k
```
