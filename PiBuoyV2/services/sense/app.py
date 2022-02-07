import glob
import json
import os
import socket
import subprocess
import time

from sense_hat import SenseHat  # pytype: disable=import-error

from hooks import insert_message_data
from hooks import send_hook


# plus 0.5 second for status per wake and plus time to run loop
MINUTES_BETWEEN_WAKES = 0.1  # roughly every 5 seconds (not 6 because of the above considerations)
MINUTES_BETWEEN_WRITES = 15
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


class Telemetry:

    def __init__(self):
        self.sense = None
        self.sensor_data = None
        self.sensor_dir = None
        self.hostname = None
        self.location = None

    def init_sense(self):
        self.sense = SenseHat()
        self.sense.clear()
        self.sense.low_light = True


    def get_temperature(self):
        # rounded to one decimal place
        return round(self.sense.get_temperature(), 1)


    def get_humidity(self):
        # rounded to one decimal place
        return round(self.sense.get_humidity(), 1)


    def get_pressure(self):
        # rounded to one decimal place
        return round(self.sense.get_pressure(), 1)


    def get_acceleration(self):
        acceleration = self.sense.get_accelerometer_raw()
        # rounded to two decimal places
        x = round(acceleration['x'], 2)
        y = round(acceleration['y'], 2)
        z = round(acceleration['z'], 2)
        return x, y, z


    def get_gyro(self):
        gyro = self.sense.get_gyroscope_raw()
        # rounded to two decimal places
        x = round(gyro['x'], 2)
        y = round(gyro['y'], 2)
        z = round(gyro['z'], 2)
        return x, y, z


    def get_compass(self):
        compass = self.sense.get_compass_raw()
        # rounded to two decimal places
        x = round(compass['x'], 2)
        y = round(compass['y'], 2)
        z = round(compass['z'], 2)
        return x, y, z


    def display(self, x, y, color):
        self.sense.set_pixel(x, y, color)


    @staticmethod
    def check_internet():
        output = subprocess.check_output("/internet_check.sh")
        if b'Online' in output:
            return True
        return False


    def check_ais(self, ais_dir, ais_file, ais_records):
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


    def check_power(self, power_dir, power_file):
        files = sorted([f for f in os.listdir(power_dir) if os.path.isfile(os.path.join(power_dir, f))])
        if not files:
            return power_file
        elif os.path.join(power_dir, files[-1]) != power_file:
            power_file = os.path.join(power_dir, files[-1])
        with open(power_file, 'r') as f:
            for line in f:
                record = json.loads(line.strip())
                if record['target'] in self.sensor_data:
                    self.sensor_data[record['target']].append(record['datapoints'][-1])
        return power_file


    def check_hydrophone(self, hydrophone_dir, hydrophone_file, hydrophone_size):
        # TODO
        return True, hydrophone_file, hydrophone_size


    def init_sensor_data(self):
        self.sensor_data = {"temperature_c": [],
                            "pressure": [],
                            "humidity": [],
                            "acceleration_x": [],
                            "acceleration_y": [],
                            "acceleration_z": [],
                            "gyroscope_x": [],
                            "gyroscope_y": [],
                            "gyroscope_z": [],
                            "compass_x": [],
                            "compass_y": [],
                            "compass_z": [],
                            "system_load": [],
                            "memory_used_mb": [],
                            "internet": [],
                            "battery": [],
                            "ais_record": [],
                            "audio_record": [],
                            "disk_free_gb": [],
                            "version": [],
                            "files_to_upload": [],
                            "data_files": [],
                            "uptime_seconds": [],
                            "battery_charge": [],
                            "battery_voltage": [],
                            "battery_current": [],
                            "battery_temperature": [],
                            "battery_status": [],
                            "power_input": [],
                            "power_input_5v": [],
                            "io_current": [],
                            "watchdog_reset": [],
                            "charging_temperature_fault": [],
                           }


    def rename_dotfiles(self):
        for dotfile in glob.glob(os.path.join(self.sensor_dir, '.*')):
            basename = os.path.basename(dotfile)
            non_dotfile = os.path.join(self.sensor_dir, basename[1:])
            os.rename(dotfile, non_dotfile)


    def write_sensor_data(self, timestamp):
        tmp_filename = f'{self.sensor_dir}/.{self.hostname}-{timestamp}-sensehat.json'
        with open(tmp_filename, 'a') as f:
            for key in self.sensor_data.keys():
                record = {"target":key, "datapoints": self.sensor_data[key]}
                f.write(f'{json.dumps(record)}\n')
        self.rename_dotfiles()
        status = self.status_hook()
        print(f'Status update response: {status}')


    def shutdown_hook(self):
        data = {}
        # TODO don't use dummy data
        data['title'] = os.path.join(self.hostname, self.location)
        data['themeColor'] = "d95f02"
        data['body_title'] = "Shutting system down"
        data['body_subtitle'] = "Low battery"
        data['text'] = ""
        data['facts'] = self.status_data()
        card = insert_message_data(data)
        status = send_hook(card)
        return status


    def status_hook(self):
        data = {}
        data['title'] = os.path.join(self.hostname, self.location)
        data['body_title'] = "Status Update"
        data['body_subtitle'] = "n / n checks healthy" # TODO replace n / n
        # TODO if not all checks are healthy
        #    data['themeColor'] = "d95f02"
        data['text'] = ""
        data['facts'] = self.status_data()
        card = insert_message_data(data)
        status = send_hook(card)
        return status


    def status_data(self):
        facts = []
        for key in self.sensor_data.keys():
            # TODO check specific keys for healthy
            if len(self.sensor_data[key]) > 0:
                facts.append({"name": key, "value": str(self.sensor_data[key][-1][0])})
        return facts


    def main(self):
        self.hostname = os.getenv("HOSTNAME", socket.gethostname())
        self.location = os.getenv("LOCATION", "unknown")
        base_dir = '/flash/telemetry'
        self.sensor_dir = os.path.join(base_dir, 'sensors')
        os.makedirs(self.sensor_dir, exist_ok=True)
        self.init_sensor_data()

        ais_dir = os.path.join(base_dir, 'ais')
        ais_file = None
        ais_records = 0
        hydrophone_dir = os.path.join(base_dir, 'hydrophone')
        hydrophone_file = None
        hydrophone_size = 0
        power_dir = os.path.join(base_dir, 'power')
        power_file = None
        s3_dir = '/flash/s3'
        s3_files = 0

        # Throwaway readings to calibrate
        for i in range(5):
            # Light up top left to indicate running calibration
            self.display(0, 0, white)
            t = self.get_temperature()
            p = self.get_pressure()
            h = self.get_humidity()
            ax, ay, az = self.get_acceleration()
            gx, gy, gz = self.get_gyro()
            cx, cy, cz = self.get_compass()

        # Turn off top left to indicate calibration is done
        self.display(0, 0, off)

        # Cycle through getting readings forever
        cycles = 1
        write_cycles = 1
        while True:
            # TODO: write out data if exception with a try/except
            timestamp = int(time.time()*1000)
            # If the middle button on the joystick is pressed, shutdown the system
            for event in self.sense.stick.get_events():
                if event.action == "released" and event.direction == "middle":
                    # TODO
                    pass

            # Light up top left pixel for cycle
            self.display(0, 0, blue)

            if cycles == CYCLES_BEFORE_STATUS_CHECK or MINUTES_BETWEEN_WAKES > 1:
                cycles = 1
                write_cycles += 1
                # TODO check other items for updates (hydrophone recordings, battery, uploads, patching, version)
                # internet: check if available
                inet = self.check_internet()
                self.sensor_data["internet"].append([inet, timestamp])
                if inet:
                    self.display(7, 7, blue)
                else:
                    self.display(7, 7, red)

                # ais: see if new detection since last cycle
                ais, ais_file, ais_records = self.check_ais(ais_dir, ais_file, ais_records)
                self.sensor_data["ais_record"].append([ais, timestamp])
                if ais:
                    self.display(7, 6, blue)
                else:
                    self.display(7, 6, yellow)

                # recordings: see if new recording file since last session, or if more bytes have been written
                hydrophone, hydrophone_file, hydrophone_size = self.check_hydrophone(hydrophone_dir, hydrophone_file, hydrophone_size)
                self.sensor_data["audio_record"].append([hydrophone, timestamp])
                if hydrophone:
                    self.display(7, 5, blue)
                else:
                    self.display(7, 5, yellow)

                # docker container health

                # uploads: see if files are gone ?

                # system health: load
                load = os.getloadavg()
                self.sensor_data["system_load"].append([load[0], timestamp])
                if load[0] > 2:
                    self.display(7, 3, red)
                elif load[0] > 1:
                    self.display(7, 3, yellow)
                else:
                    self.display(7, 3, blue)

                # system health: memory
                total_memory, used_memory, free_memory = map(int, os.popen('free -t -m').readlines()[1].split()[1:])
                self.sensor_data["memory_used_mb"].append([used_memory, timestamp])
                if used_memory/total_memory > 0.9:
                    self.display(7, 2, red)
                elif used_memory/total_memory > 0.7:
                    self.display(7, 2, yellow)
                else:
                    self.display(7, 2, blue)

                # system health: disk space
                st = os.statvfs('/')
                bytes_avail = (st.f_bavail * st.f_frsize)
                gb_free = round(bytes_avail / 1024 / 1024 / 1024, 1)
                self.sensor_data["disk_free_gb"].append([gb_free, timestamp])
                if gb_free < 2:
                    self.display(6, 7, red)
                elif gb_free < 10:
                    self.display(6, 7, yellow)
                else:
                    self.display(6, 7, blue)

                # system uptime (linux only!)
                self.sensor_data["uptime_seconds"].append([time.clock_gettime(time.CLOCK_BOOTTIME), timestamp])

                # battery: check current battery level from pijuice hopefully, change color based on level
                power_file = self.check_power(power_dir, power_file)

                # version: updated?

            # Take readings from sensors
            t = self.get_temperature()
            self.sensor_data["temperature_c"].append([t, timestamp])
            if t < 5 or t > 70:
                self.display(1, 0, red)
            elif t < 10 or t > 65:
                self.display(1, 0, yellow)
            else:
                self.display(1, 0, blue)
            p = self.get_pressure()
            self.sensor_data["pressure"].append([p, timestamp])
            self.display(2, 0, blue)
            h = self.get_humidity()
            self.sensor_data["humidity"].append([h, timestamp])
            self.display(3, 0, blue)
            ax, ay, az = self.get_acceleration()
            self.sensor_data["acceleration_x"].append([ax, timestamp])
            self.sensor_data["acceleration_y"].append([ay, timestamp])
            self.sensor_data["acceleration_z"].append([az, timestamp])
            self.display(4, 0, blue)
            gx, gy, gz = self.get_gyro()
            self.sensor_data["gyroscope_x"].append([gx, timestamp])
            self.sensor_data["gyroscope_y"].append([gy, timestamp])
            self.sensor_data["gyroscope_z"].append([gz, timestamp])
            self.display(5, 0, blue)
            cx, cy, cz = self.get_compass()
            self.sensor_data["compass_x"].append([cx, timestamp])
            self.sensor_data["compass_y"].append([cy, timestamp])
            self.sensor_data["compass_z"].append([cz, timestamp])
            self.display(6, 0, blue)

            # Write out data
            if write_cycles == MINUTES_BETWEEN_WRITES:
                write_timestamp = int(time.time())
                self.write_sensor_data(write_timestamp)
                self.init_sensor_data()
                write_cycles = 1

            # Keep lights for 0.5 second
            time.sleep(0.5)

            # Turn off all pixels
            self.sense.set_pixels([off]*64)

            # Sleep between cycles
            time.sleep(60*MINUTES_BETWEEN_WAKES)

            cycles += 1


t = Telemetry()
t.init_sense()
t.main()
