import glob
import json
import os
import socket
import subprocess
import time

import docker
from sense_hat import SenseHat  # pytype: disable=import-error

from hooks import insert_message_data
from hooks import send_hook


# Raw colors
red = (255, 0, 0)
yellow = (255, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
off = (0, 0, 0)


class Telemetry:

    def __init__(self, base_dir='/flash/telemetry'):
        # plus 0.5 second for status per wake and plus time to run loop
        self.MINUTES_BETWEEN_WAKES = 0.1  # roughly every 5 seconds (not 6 because of the above considerations)
        self.MINUTES_BETWEEN_WRITES = 15
        self.CYCLES_BEFORE_STATUS_CHECK = 1/self.MINUTES_BETWEEN_WAKES
        # if waking up less than once a minute, just set the status check to the same amount of time as the wake cycle
        if self.CYCLES_BEFORE_STATUS_CHECK < 1:
            self.CYCLES_BEFORE_STATUS_CHECK = self.MINUTES_BETWEEN_WAKES

        self.hostname = os.getenv("HOSTNAME", socket.gethostname())
        self.location = os.getenv("LOCATION", "unknown")
        self.version = os.getenv("VERSION", "")
        self.sensor_dir = os.path.join(base_dir, 'sensors')
        self.ais_dir = os.path.join(base_dir, 'ais')
        self.hydrophone_dir = os.path.join(base_dir, 'hydrophone')
        self.power_dir = os.path.join(base_dir, 'power')
        self.s3_dir = '/flash/s3'
        self.ais_file = None
        self.ais_records = 0
        self.hydrophone_file = None
        self.hydrophone_size = 0
        self.power_file = None
        self.sense = None
        self.sensor_data = None
        self.alerts = {}
        self.docker = docker.from_env()

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

    def read_sensors(self, timestamp):
        t = self.get_temperature()
        self.sensor_data["temperature_c"].append([t, timestamp])
        if t < 5 or t > 70:
            self.display(6, 3, red)
            self.alerts['temperature_c'] = True
        elif t < 10 or t > 65:
            self.display(6, 3, yellow)
            self.alerts['temperature_c'] = False
        else:
            self.display(6, 3, blue)
            self.alerts['temperature_c'] = False
        p = self.get_pressure()
        self.sensor_data["pressure"].append([p, timestamp])
        self.display(5, 3, blue)
        h = self.get_humidity()
        self.sensor_data["humidity"].append([h, timestamp])
        self.display(4, 3, blue)
        ax, ay, az = self.get_acceleration()
        self.sensor_data["acceleration_x"].append([ax, timestamp])
        self.sensor_data["acceleration_y"].append([ay, timestamp])
        self.sensor_data["acceleration_z"].append([az, timestamp])
        self.display(6, 4, blue)
        gx, gy, gz = self.get_gyro()
        self.sensor_data["gyroscope_x"].append([gx, timestamp])
        self.sensor_data["gyroscope_y"].append([gy, timestamp])
        self.sensor_data["gyroscope_z"].append([gz, timestamp])
        self.display(5, 4, blue)
        cx, cy, cz = self.get_compass()
        self.sensor_data["compass_x"].append([cx, timestamp])
        self.sensor_data["compass_y"].append([cy, timestamp])
        self.sensor_data["compass_z"].append([cz, timestamp])
        self.display(4, 4, blue)

    @staticmethod
    def check_internet():
        try:
            output = subprocess.check_output("/internet_check.sh")
        except Exception as e:
            print(f'Failed to check internet because: {e}')
            output = b'Failed'

        if b'Online' in output:
            return True
        return False

    @staticmethod
    def reorder_dots(files):
        last_dot = -1
        for i, f in enumerate(files):
            if f.startswith('.'):
                last_dot = i
        last_dot += 1
        files = files[last_dot:] + files[0:last_dot]
        return files

    def check_ais(self):
        # check for new files, in the newest file, check if the number of lines has increased
        files = sorted([f for f in os.listdir(self.ais_dir) if os.path.isfile(os.path.join(self.ais_dir, f))])

        # check for dotfiles
        files = self.reorder_dots(files)

        if not files:
            self.ais_file = None
            self.ais_records = 0
            return False
        elif os.path.join(self.ais_dir, files[-1]) != self.ais_file:
            self.ais_file = os.path.join(self.ais_dir, files[-1])
            self.ais_records = sum(1 for line in open(self.ais_file))
            return True
        # file already exists, check if there's new records
        num_lines = sum(1 for line in open(self.ais_file))
        if num_lines > self.ais_records:
            self.ais_records = num_lines
            return True
        return False

    def check_power(self):
        files = sorted([f for f in os.listdir(self.power_dir) if os.path.isfile(os.path.join(self.power_dir, f))])

        # check for dotfiles
        files = self.reorder_dots(files)

        if not files:
            self.power_file = None
            return
        elif os.path.join(self.power_dir, files[-1]) != self.power_file:
            self.power_file = os.path.join(self.power_dir, files[-1])
        with open(self.power_file, 'r') as f:
            for line in f:
                record = json.loads(line.strip())
                if record['target'] in self.sensor_data:
                    self.sensor_data[record['target']].append(record['datapoints'][-1])

    def check_hydrophone(self):
        files = sorted([f for f in os.listdir(self.hydrophone_dir) if os.path.isfile(os.path.join(self.hydrophone_dir, f))])

        # check for dotfiles
        files = self.reorder_dots(files)

        # no files
        if not files:
            self.hydrophone_file = None
            self.hydrophone_size = 0
            return False
        # found a new file
        elif os.path.join(self.hydrophone_dir, files[-1]) != self.hydrophone_file:
            self.hydrophone_file = os.path.join(self.hydrophone_dir, files[-1])
            self.hydrophone_size = os.path.getsize(self.hydrophone_file)
            return True
        # file already exists, check the size
        size = os.path.getsize(self.hydrophone_file)
        if size > self.hydrophone_size:
            self.hydrophone_size = size
            return True
        return False

    def check_s3(self):
        files = sorted([f for f in os.listdir(self.s3_dir) if os.path.isfile(os.path.join(self.s3_dir, f))])
        if not files:
            return False, 0
        else:
            return True, len(files)

    def get_container_version(self, container):
        env_vars = container.attrs['Config']['Env']
        for env_var in env_vars:
            if env_var.startswith("VERSION="):
                return env_var.split("=")[-1]
        return ""

    def check_version(self, timestamp):
        self.sensor_data["version_sense"].append([self.version, timestamp])
        containers = ["ais", "power", "record", "s3-upload"]
        healthy = True
        for container in containers:
            try:
                container = self.docker.containers.get("pibuoyv2_"+container+"_1")
                if container.status != 'running':
                    healthy = False
                self.sensor_data["version_"+container].append(
                    [self.get_container_version(container), timestamp])
            except Exception as e:
                self.sensor_data["version_"+container].append([str(e), timestamp])
                healthy = False
        return healthy

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
                            "files_to_upload": [],
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
                            "version_ais": [],
                            "version_power": [],
                            "version_record": [],
                            "version_s3-upload": [],
                            "version_sense": [],
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

    def shutdown_hook(self, subtitle):
        data = {}
        data['title'] = os.path.join(self.hostname, self.location)
        data['themeColor'] = "d95f02"
        data['body_title'] = "Shutting system down"
        data['body_subtitle'] = subtitle
        data['text'] = ""
        data['facts'] = self.status_data()
        card = insert_message_data(data)
        status = send_hook(card)
        return status

    def status_hook(self):
        checks = len(self.alerts)
        health = 0
        unhealthy = []
        for alert in self.alerts:
            if self.alerts[alert]:
                unhealthy.append(alert)
            else:
                health += 1

        data = {}
        data['title'] = os.path.join(self.hostname, self.location)
        data['body_title'] = "Status Update"
        data['body_subtitle'] = f'{health} / {checks} checks healthy'
        if health < checks:
            data['themeColor'] = "d95f02"
        data['text'] = f'Checks that alerted: {unhealthy}'
        data['facts'] = self.status_data()
        card = insert_message_data(data)
        status = send_hook(card)
        return status

    def status_data(self):
        facts = []
        for key in self.sensor_data.keys():
            if len(self.sensor_data[key]) > 0:
                facts.append({"name": key, "value": str(self.sensor_data[key][-1][0])})
        return facts

    def run_checks(self, timestamp):
        # internet: check if available
        inet = self.check_internet()
        self.sensor_data["internet"].append([inet, timestamp])
        if inet:
            self.display(5, 7, blue)
            self.alerts['internet'] = False
        else:
            self.display(5, 7, red)
            self.alerts['internet'] = True

        # version and docker container health:
        healthy = self.check_version(timestamp)
        if healthy:
            self.display(4, 7, blue)
            self.alerts['healthy'] = False
        else:
            self.display(4, 7, red)
            self.alerts['healthy'] = True

        # ais: see if new detection since last cycle
        ais = self.check_ais()
        self.sensor_data["ais_record"].append([ais, timestamp])
        if ais:
            self.display(6, 5, blue)
        else:
            self.display(6, 5, white)

        # recordings: see if new recording file since last session, or if more bytes have been written
        hydrophone = self.check_hydrophone()
        self.sensor_data["audio_record"].append([hydrophone, timestamp])
        if hydrophone:
            self.display(5, 5, blue)
        else:
            self.display(5, 5, white)

        # files to upload to s3
        s3, s3_files = self.check_s3()
        self.sensor_data["files_to_upload"].append([s3_files, timestamp])
        if s3:
            self.display(4, 5, blue)
        else:
            self.display(4, 5, white)

        # system health: load
        load = os.getloadavg()
        self.sensor_data["system_load"].append([load[0], timestamp])
        if load[0] > 2:
            self.display(6, 6, red)
            self.alerts['system_load'] = True
        elif load[0] > 1:
            self.display(6, 6, yellow)
            self.alerts['system_load'] = False
        else:
            self.display(6, 6, blue)
            self.alerts['system_load'] = False

        # system health: memory
        total_memory, used_memory, free_memory = map(int, os.popen('free -t -m').readlines()[1].split()[1:4])
        self.sensor_data["memory_used_mb"].append([used_memory, timestamp])
        if used_memory/total_memory > 0.9:
            self.display(5, 6, red)
            self.alerts['memory_used_mb'] = True
        elif used_memory/total_memory > 0.7:
            self.display(5, 6, yellow)
            self.alerts['memory_used_mb'] = False
        else:
            self.display(5, 6, blue)
            self.alerts['memory_used_mb'] = False

        # system health: disk space
        st = os.statvfs('/')
        bytes_avail = (st.f_bavail * st.f_frsize)
        gb_free = round(bytes_avail / 1024 / 1024 / 1024, 1)
        self.sensor_data["disk_free_gb"].append([gb_free, timestamp])
        if gb_free < 2:
            self.display(4, 6, red)
            self.alerts['disk_free_gb'] = True
        elif gb_free < 10:
            self.display(4, 6, yellow)
            self.alerts['disk_free_gb'] = False
        else:
            self.display(4, 6, blue)
            self.alerts['disk_free_gb'] = False

        # system uptime (linux only!)
        self.sensor_data["uptime_seconds"].append([time.clock_gettime(time.CLOCK_BOOTTIME), timestamp])

        # battery: check current battery level from pijuice hopefully, change color based on level
        self.check_power()
        if len(self.sensor_data['battery_status']) > 0:
            if self.sensor_data['battery_status'][-1][0] == 'NORMAL':
                self.display(7, 3, blue)
                self.alerts['battery_status'] = False
            elif self.sensor_data['battery_status'][-1][0] == 'CHARGING_FROM_IN':
                self.display(7, 3, yellow)
                self.alerts['battery_status'] = False
            else:
                self.display(7, 3, red)
                self.alerts['battery_status'] = True
        else:
            self.display(7, 3, white)
        if len(self.sensor_data['battery_charge']) > 0:
            if int(self.sensor_data['battery_charge'][-1][0]) > 50:
                self.display(7, 4, blue)
                self.alerts['battery_charge'] = False
            elif int(self.sensor_data['battery_charge'][-1][0]) > 20:
                self.display(7, 4, yellow)
                self.alerts['battery_charge'] = False
            else:
                self.display(7, 4, red)
                self.alerts['battery_charge'] = True
        else:
            self.display(7, 4, white)
        if len(self.sensor_data['power_input']) > 0:
            if self.sensor_data['power_input'][-1][0] == 'PRESENT':
                self.display(7, 5, blue)
            else:
                self.display(7, 5, yellow)
        else:
            self.display(7, 5, white)

    def main(self, run_forever):
        os.makedirs(self.sensor_dir, exist_ok=True)
        self.init_sensor_data()

        # Throwaway readings to calibrate
        for i in range(5):
            # Light up top left to indicate running calibration
            self.display(7, 7, white)
            t = self.get_temperature()
            p = self.get_pressure()
            h = self.get_humidity()
            ax, ay, az = self.get_acceleration()
            gx, gy, gz = self.get_gyro()
            cx, cy, cz = self.get_compass()

        # Turn off top left to indicate calibration is done
        self.display(7, 7, off)

        # Cycle through getting readings forever
        cycles = 1
        write_cycles = 1
        user_shutdown = False
        running = True
        while running:
            running = run_forever

            # TODO: write out data if exception with a try/except
            timestamp = int(time.time()*1000)

            # If the middle button on the joystick is pressed, shutdown the system
            for event in self.sense.stick.get_events():
                if event.action == "released" and event.direction == "middle":
                    user_shutdown = True
                    self.shutdown_hook("User initiated")
                    try:
                        subprocess.run("/shutdown.sh")
                    except Exception as e:
                        print(f'Failed to shutdown because: {e}')

            # Check if a shutdown has been signaled
            signal_contents = ""
            try:
                with open('/var/run/shutdown.signal', 'r') as f:
                    signal_contents = f.read()
            except Exception as e:
                pass

            # Light up top left pixel for cycle
            self.display(7, 7, blue)

            if signal_contents.strip() == 'true':
                self.display(7, 7, red)
                if not user_shutdown:
                    self.shutdown_hook("Low battery")
                    user_shutdown = True

            if cycles == self.CYCLES_BEFORE_STATUS_CHECK or self.MINUTES_BETWEEN_WAKES > 1:
                self.run_checks(timestamp)
                cycles = 1
                write_cycles += 1

            # Take readings from sensors
            self.read_sensors(timestamp)

            # Write out data
            if write_cycles == self.MINUTES_BETWEEN_WRITES:
                write_timestamp = int(time.time())
                self.write_sensor_data(write_timestamp)
                self.init_sensor_data()
                write_cycles = 1

            # Keep lights for 0.5 second
            time.sleep(0.5)

            # Turn off all pixels
            self.sense.set_pixels([off]*64)

            # Sleep between cycles
            time.sleep(60*self.MINUTES_BETWEEN_WAKES)

            cycles += 1


if __name__ == '__main__':
    t = Telemetry()
    t.init_sense()
    t.main(True)
