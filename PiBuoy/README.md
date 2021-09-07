The following are the hardware and software requirements and installation instructions for the Raspberry Pi 4 buoy version.

# Hardware Requirements

TODO

# Hardware configuration installation

1. [Flash SleepyPi](sleepypi/README.md)

2. Configure Sixfab/telit/quectel/sim card/cut jumper for GPIO conflict - TODO

3. Wire sleepypi

4. Wire sensehat

# Initial installation

1. Install Raspbian (buster) on the SD card for the Raspberry Pi.

2. Put the [config.txt](config/config.txt) in `/boot/config.txt`. Reboot.

3. If using a USB flash drive (recommended) format and mount the drive as follows as `root`, otherwise just ensure `/flash` exists with `mkdir -p /flash`:

```
fdisk -l
```
Find the disk that corresponds to your USB flash drive, likely something like `/dev/sda`:
```
fdisk /dev/sda

d  (deletes the current partition)
n  (create a new partition)
p  (specify the new partition as primary)
1  (set it as the 1st position)
w  (write out changes)
```
* Note: use defaults unless you want to size it differently for some reason

Ensure the new partition shows up correctly:
```
fdisk -l
```
Make the filesystem on the partition:
```
mkfs -t ext4 /dev/sda1
mkdir -p /flash
```
To ensure this filesystem gets mounted on reboot, add it to `/etc/fstab`:
```
# get the UUID of the disk partition
blkid
```
Edit `/etc/fstab` with your favorite editor and add the following line:
```
UUID=<insert uuid from blkid here> /flash ext4 defaults,auto,users,rw,nofail 0 0
```

4. Install required packages.
```
sudo apt-get update
sudo apt-get install alsa-utils curl ffmpeg git python3-pip tmux screen libglib2.0-dev i2c-tools
```

5. Install gpsd 3.23 from source following instructions [here](https://gpsd.gitlab.io/gpsd/installation.html)

6. Install this repo.
```
sudo su -
cd /opt
git clone https://github.com/IQTLabs/AISonobuoy.git
```

7. Install required Python packages.
```
cd /opt/AISonobuoy/PiBuoy/scripts
sudo pip3 install -r requirements.txt
```

8. Set WLAN Country using `sudo raspi-config`.

9. Disable `gpsd` service.
```
sudo systemctl disable gpsd.service
```

10. Install pindrop with modifications.
```
git clone https://github.com/needmorecowbell/pindrop.git
cd pindrop
git apply -v /opt/AISonobuoy/PiBuoy/scripts/pindrop.diff
sudo python3 setup.py install
```

11. Setup [Sixfab](https://docs.sixfab.com/page/setting-up-the-ppp-connection-for-sixfab-shield-hat) for PPP.
```
wget https://raw.githubusercontent.com/sixfab/Sixfab_PPP_Installer/master/ppp_install_standalone.sh
sudo chmod +x ppp_install_standalone.sh
sudo ./ppp_install_standalone.sh
```

12. Setup [dAISy HAT](https://wegmatt.com/files/dAISy%20HAT%20AIS%20Receiver%20Manual.pdf).
```
wget https://github.com/itemir/rpi_boat_utils/raw/master/uart_control/uart_control
chmod +x ./uart_control
sudo ./uart_control gpio
```

13. Install services.
```
sudo cp /opt/AISonobuoy/PiBuoy/config/*.service /etc/systemd/system/
sudo cp /opt/AISonobuoy/PiBuoy/sleepypid/sleepypid.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sleepypid.service
sudo systemctl enable pindrop.service
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
1. Check logs in `/var/log/syslog`, `/var/log/messages`, /var/log/sleepypid.log`.

2. Check `dmesg` for errors.

3. Check for data in `/flash/telemetry`.

4. Check internet connection on interface `ppp0`.
```
ifconfig ppp0
ping -I ppp0 google.com
```

5. Check serial connection for AIS.
```
sudo screen /dev/serial0 38400
<press ESC> (you should see a menu)
<press ESC>
<ctrl>+a k
```

6. Check serial connection for SleepyPi.
```
sudo screen /dev/ttyAMA1 9600
{} (it should reply with a JSON response)
<ctrl>+a k
```
