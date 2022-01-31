The following are the hardware and software requirements and installation instructions for the Raspberry Pi 4 buoy version.

# Hardware Requirements

- Raspberry Pi Zero 2 W
- HiFiBerry DAC+ADC Pro
- dAISy HAT
- Sense HAT
- PiJuice Zero
- pHAT Stack
- 12000mAh PiJuice Battery

# Hardware configuration installation

1. Solder Pi Zero 2 W stacking header.

2. Add Mic Bias jumpers to the HiFiBerry HAT.

3. Remove pin 12 from the header attached to the dAISy HAT.

# Initial installation

1. Install Raspberry Pi OS (choose 'Raspberry Pi OS other' and then 'Raspberry Pi OS Lite 32-bit' based on Debian Bullseye) on the SD card for the Raspberry Pi using Raspberry Pi Imager.
- Use `CTRL+SHIFT+x` to use advanced options when flashing the SD card. Set the hostname, enable SSH and add a password or key, configure WiFi and set the correct WiFi country, set the locale settings and Skip the first-run wizard.

2. Install required packages.
```
sudo apt-get update
sudo apt-get install git python3-pip screen tmux
```

3. Install this repo.
```
sudo su -
cd /opt
git clone https://github.com/IQTLabs/AISonobuoy.git
```

4. Install Docker.
```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi
```

5. Install docker-compose.
```
sudo pip3 install docker-compose
```

6. Put the config.txt in `/boot/config.txt`.
```
sudo cp /opt/AISonobuoy/PiBuoyV2/config/config.txt /boot/config.txt
```

7. Setup [dAISy HAT](https://wegmatt.com/files/dAISy%20HAT%20AIS%20Receiver%20Manual.pdf).
```
wget https://github.com/itemir/rpi_boat_utils/raw/master/uart_control/uart_control
chmod +x ./uart_control
sudo ./uart_control gpio
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
1 * * * * /usr/bin/git -C /opt/AISonobuoy pull
```

9. Add [AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) using `aws configure`.

10. Enable I2C in raspi-config.
```
sudo raspi-config
-> Interface Options -> I2C -> Yes to enable
```

11. Restart.
```
sudo reboot
```

12. Start PiBuoy containers.
```
cd /opt/AISonobuoy/PiBuoyV2
docker-compose up -d
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
