The following are the hardware and software requirements and installation instructions for the Raspberry Pi 4 buoy version.

# Hardware Requirements

TODO

# Hardware configuration installation

1. Solder Pi Zero 2 W stacking header

2. Add Mic Bias jumpers to the HiFiBerry hat.

# Initial installation

1. Install Raspberry Pi OS (choose 'Raspberry Pi OS other' and then 'Raspberry Pi OS Lite 32-bit' based on Debian Bullseye) on the SD card for the Raspberry Pi using Raspberry Pi Imager.
- Use `CTRL+SHIFT+x` to use advanced options when flashing the SD card. Set the hostname, enable SSH and add a password or key, configure WiFi and set the correct WiFi country, set the locale settings and Skip the first-run wizard.


2. Install required packages.
```
sudo apt-get update
sudo apt-get install curl ffmpeg git libatlas-base-dev libglib2.0-dev python3-pip python3-rtimulib screen tmux
```

3. Install this repo.
```
sudo su -
cd /opt
git clone https://github.com/IQTLabs/AISonobuoy.git
```

4. Put the config.txt in `/boot/config.txt`.
```
sudo cp /opt/AISonobuoy/PiBuoyV2/config/config.txt /boot/config.txt
```

5. Install required Python packages.
```
cd /opt/AISonobuoy/PiBuoyV2/scripts
sudo python3 -m pip install -U pip
sudo pip3 install -r requirements.txt
```

6. Setup [dAISy HAT](https://wegmatt.com/files/dAISy%20HAT%20AIS%20Receiver%20Manual.pdf).
```
wget https://github.com/itemir/rpi_boat_utils/raw/master/uart_control/uart_control
chmod +x ./uart_control
sudo ./uart_control gpio
```

7. Install services.
```
sudo cp /opt/AISonobuoy/PiBuoyV2/config/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ais.service
sudo systemctl enable record.service
sudo systemctl enable s_hat.service
```

8. Schedule jobs in crontab.
```
sudo crontab -e
```
Add the following lines, save, and quit:
```
# every five minutes
*/5 * * * * /opt/AISonobuoy/PiBuoyV2/scripts/system_health.sh
# once an hour, one minute past the hour
1 * * * * /usr/bin/env bash /opt/AISonobuoy/PiBuoyV2/scripts/s3_prep.sh
@reboot /opt/AISonobuoy/PiBuoyV2/scripts/startup.sh
1 * * * * /usr/bin/git -C /opt/AISonobuoy pull
```

9. Edit the `s3://` path in `/opt/AISonobuoy/PiBuoyV2/scripts/s3_prep.sh` to be an S3 bucket you want to push data to.

10. Add [AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) using `aws configure`.

11. Remove pulseaudio.

```
sudo apt-get remove pulseaudio
sudo apt-get autoremove
```

12. Add asound.conf under configs to `/etc/asound.conf`
```
sudo cp /opt/AISonobuoy/PiBuoyV2/config/asound.conf /etc/asound.conf
```

13. Enable I2C in raspi-config.
```
sudo raspi-config
-> Interface Options -> I2C -> Yes to enable
```

14. Restart.
```
sudo reboot
```

15. Set ADC settings for HiFiBerry hat.
```
amixer sset "ADC Mic Bias" "Mic Bias on"
amixer sset "ADC Left Input" "VINL1[SE]"
amixer sset "ADC Right Input" "VINR1[SE]"
amixer sset ADC 40db
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
