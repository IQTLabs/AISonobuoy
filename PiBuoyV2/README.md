The following are the hardware and software requirements and installation instructions for the Raspberry Pi 4 buoy version.

# Hardware Requirements

TODO

# Hardware configuration installation

4. Wire sensehat

5. Solder HifiBerry header

# Initial installation

1. Install Raspberry Pi OS on the SD card for the Raspberry Pi.

2. Put the [config.txt](config/config.txt) in `/boot/config.txt`. Reboot.

4. Install required packages.
```
sudo apt-get update
sudo apt-get install curl ffmpeg tmux screen libglib2.0-dev
```

6. Install this repo.
```
sudo su -
cd /opt
git clone https://github.com/IQTLabs/AISonobuoy.git
```

7. Install required Python packages.
```
cd /opt/AISonobuoy/PiBuoyV2/scripts
sudo pip3 install -r requirements.txt
```

8. Set WLAN Country using `sudo raspi-config`.

12. Setup [dAISy HAT](https://wegmatt.com/files/dAISy%20HAT%20AIS%20Receiver%20Manual.pdf).
```
wget https://github.com/itemir/rpi_boat_utils/raw/master/uart_control/uart_control
chmod +x ./uart_control
sudo ./uart_control gpio
```

13. Install services.
```
sudo cp /opt/AISonobuoy/PiBuoy/config/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ais.service
sudo systemctl enable record.service
```

14. Schedule jobs in crontab.
```
sudo crontab -e
```
Add the following lines, save, and quit:
```
# every five minutes
*/5 * * * * /opt/AISonobuoy/PiBuoy/scripts/system_health.sh
2-59/5 * * * * python3 /opt/AISonobuoy/PiBuoy/sense_hat_b/LPS22HB.py
3-59/5 * * * * python3 /opt/AISonobuoy/PiBuoy/sense_hat_b/ICM20948.py
4-59/5 * * * * python3 /opt/AISonobuoy/PiBuoy/sense_hat_b/SHTC3.py
# once an hour, one minute past the hour
1 * * * * /usr/bin/env bash /opt/AISonobuoy/PiBuoy/scripts/s3_prep.sh
```

15. Edit the `s3://` path in `/opt/AISonobuoy/PiBuoy/scripts/s3_prep.sh` to be an S3 bucket you want to push data to.

16. Add [AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) using `aws configure`.

17. Set hostname using `sudo raspi-config`.

18. Restart.
```
sudo reboot
```

# Verify components are working
1. Check logs in `/var/log/syslog`, `/var/log/messages`.

2. Check `dmesg` for errors.

3. Check for data in `/flash/telemetry`.

5. Check serial connection for AIS.
```
sudo screen /dev/serial0 38400
<press ESC> (you should see a menu)
<press ESC>
<ctrl>+a k
```
