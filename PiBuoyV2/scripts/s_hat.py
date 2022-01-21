from sense_hat import SenseHat

import os
import subprocess
import time


# Initialize the Sense Hat
sense = SenseHat()
sense.clear()
sense.low_light = True

# plus 0.5 second for status per wake and plus time to run loop
MINUTES_BETWEEN_WAKES = 0.1  # roughly every 5 seconds (not 6 because of the above considerations)
CYCLES_BEFORE_STATUS_CHECK = 1/MINUTES_BETWEEN_WAKES
# if waking up less than once a minute, just set the status check to the same amount of time as the wake cycle
if CYCLES_BEFORE_STATUS_CHECK < 1:
    CYCLES_BEFORE_STATUS_CHECK = MINUTES_BETWEEN_WAKES

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
    output = subprocess.check_output("/opt/AISonobuoy/PiBuoyV2/scripts/internet_check.sh")
    if b'Online' in output:
        return True
    return False


def check_ais(ais_dir, ais_file, ais_records):
    # check for new files, in the newest file, check if the number of lines has increased
    files = sorted([f for f in os.listdir(ais_dir) if os.path.isfile(os.path.join(ais_dir, f))])
    if not files:
        return False, ais_file, ais_records
    elif os.path.join(ais_dir, files[-1]) != ais_file:
        ais_file = os.path.join(ais_dir, files[-1])
        ais_records = sum(1 for line in open(ais_file))
        return True, ais_file, ais_records
    # file already exists, check if there's new records
    num_lines = sum(1 for line in open(ais_file))
    if num_lines > ais_records:
        ais_records = num_lines
        return True, ais_file, ais_records
    return False, ais_file, ais_records


def main():
    # TODO initial status states
    ais_dir = '/flash/telemetry/ais'
    ais_file = None
    ais_records = 0
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
    cycles = 1
    while True:
        # If the middle button on the joystick is pressed, shutdown the system
        for event in sense.stick.get_events():
            if event.action == "released" and event.direction == "middle":
                subprocess.run("/opt/AISonobuoy/PiBuoyV2/scripts/shutdown.sh")

        # Light up top left pixel for cycle
        display(0, 0, blue)

        if cycles == CYCLES_BEFORE_STATUS_CHECK or MINUTES_BETWEEN_WAKES > 1:
            cycles = 1
            # TODO check other items for updates (load/memory?, hydrophone recordings, battery, uploads, patching)
            # internet: check if available
            inet = check_internet()
            if inet:
                display(7, 7, blue)
            else:
                display(7, 7, red)

            # ais: see if new detection since last cycle
            ais, ais_file, ais_records = check_ais(ais_dir, ais_file, ais_records)
            if ais:
                display(7, 6, blue)
            else:
                display(7, 6, yellow)

            # recordings: see if new recording file since last session, or see if process to record is running

            # uploads: see if files are gone ?

            # system health: load
            load = os.getloadavg()
            if load[0] > 2:
                display(7, 3, red)
            elif load[0] > 1:
                display(7, 3, yellow)
            else:
                display(7, 3, blue)

            # system health: memory
            total_memory, used_memory, free_memory = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
            if used_memory/total_memory > 0.9:
                display(7, 2, red)
            elif used_memory/total_memory > 0.7:
                display(7, 2, yellow)
            else:
                display(7, 2, blue)

            # battery: check current battery level from pijuice hopefully, change color based on level

            # patching: run update file which should do everything including restarting services or rebooting

        # Take readings from sensors
        t = get_temperature()
        display(1, 0, blue)
        p = get_pressure()
        display(2, 0, blue)
        h = get_humidity()
        display(3, 0, blue)
        ax, ay, az = get_acceleration()
        display(4, 0, blue)
        gx, gy, gz = get_gyro()
        display(5, 0, blue)
        cx, cy, cz = get_compass()
        display(6, 0, blue)

        # TODO store data

        # Keep lights for 0.5 second
        time.sleep(0.5)

        # Turn off all pixels
        sense.set_pixels([off]*64)

        # sleep between cycles
        time.sleep(60*MINUTES_BETWEEN_WAKES)

        cycles += 1


main()
