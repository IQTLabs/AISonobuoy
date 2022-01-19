from sense_hat import SenseHat

import time
import subprocess


# Initialize the Sense Hat
sense = SenseHat()
sense.clear()
sense.low_light = True

# plus 0.5 second for status per wake and plus time to run loop
MINUTES_BETWEEN_WAKES = 0.1  # roughly every 5 seconds

# Define Colors
# (generated from ColorBrewer)
# Credit: Cynthia Brewer, Mark Harrower and The Pennsylvania State University
cb_orange = (252, 141, 89)
cb_yellow = (255, 255, 191)
cb_blue = (145, 191, 219)

# Raw colors
red = (255, 0, 0)
yellow = (255, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
off = (0, 0, 0)


def get_temperature():
    # rounded to one decimal place
    return round(sense.get_temperature(), 1)


def get_humidity():
    # rounded to one decimal place
    return round(sense.get_humidity(), 1)


def get_pressure():
    # rounded to one decimal place
    return round(sense.get_pressure(), 1)


def get_acceleration():
    acceleration = sense.get_accelerometer_raw()
    # rounded to two decimal places
    x = round(acceleration['x'], 2)
    y = round(acceleration['y'], 2)
    z = round(acceleration['z'], 2)
    return x, y, z


def get_gyro():
    gyro = sense.get_gyroscope_raw()
    # rounded to two decimal places
    x = round(gyro['x'], 2)
    y = round(gyro['y'], 2)
    z = round(gyro['z'], 2)
    return x, y, z


def get_compass():
    compass = sense.get_compass_raw()
    # rounded to two decimal places
    x = round(compass['x'], 2)
    y = round(compass['y'], 2)
    z = round(compass['z'], 2)
    return x, y, z


def display(x, y, color):
    sense.set_pixel(x, y, color)


def check_internet():
    output = subprocess.check_output(["bash", "/opt/AISonoBuoy/PiBuoyV2/scripts/internet_check.sh"])
    if "Online" in output:
        return True
    return False


def main():
    # TODO initial status states
    ais_file = None
    recording_file = None
    uploads = None

    # Throwaway readings to calibrate
    for i in range(5):
        # Light up top left to indicate running calibration
        display(0, 0, white)
        t = get_temperature()
        p = get_pressure()
        h = get_humidity()
        ax, ay, az = get_acceleration()
        gx, gy, gz = get_gyro()
        cx, cy, cz = get_compass()

    # Turn off top left to indicate calibration is done
    display(0, 0, off)

    # Cycle through getting readings forever
    while True:
        # Light up bottom right pixel for status
        display(7, 7, blue)

        # TODO check other items for updates (ais, hydrophone recordings, battery, uploads, patching, internet connection)
        # internet update
        inet = check_internet()
        if inet:
            display(7, 6, blue)
        else:
            display(7, 6, red)

        # patching: run update file which should do everything including restarting services or rebooting

        # ais: see if new detection since last cycle

        # recordings: see if new recording file since last session, or see if process to record is running

        # battery: check current battery level from pijuice hopefully, change color based on level

        # uploads: see if files are gone ?

        # Take readings from sensors
        t = get_temperature()
        p = get_pressure()
        h = get_humidity()
        ax, ay, az = get_acceleration()
        gx, gy, gz = get_gyro()
        cx, cy, cz = get_compass()

        # TODO store data

        # Keep lights for 0.5 second
        time.sleep(0.5)

        # Turn off pixels for status
        display(7, 6, off)
        display(7, 7, off)

        # sleep between cycles
        time.sleep(60*MINUTES_BETWEEN_WAKES)


main()
