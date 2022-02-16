import glob
import json
import os
import shutil
import socket
import time


class Power:

    def __init__(self):
        self.hostname = os.getenv("HOSTNAME", socket.gethostname())
        self.data_dir = '/flash/telemetry/power'

    def rename_dotfiles(self):
        for dotfile in glob.glob(os.path.join(self.data_dir, '.*')):
            basename = os.path.basename(dotfile)
            non_dotfile = os.path.join(self.data_dir, basename[1:])
            os.rename(dotfile, non_dotfile)

    def write_data(self, timestamp, data):
        tmp_filename = f'{self.data_dir}/.{self.hostname}-{timestamp}-power.json'
        with open(tmp_filename, 'a') as f:
            for key in data.keys():
                record = {"target":key, "datapoints": data[key]}
                f.write(f'{json.dumps(record)}\n')
        self.rename_dotfiles()

    @staticmethod
    def init_data():
        pijuice_data = {"battery_charge": [],
                        "battery_voltage": [],
                        "battery_current": [],
                        "battery_temperature": [],
                        "battery_status": [],
                        "power_input": [],
                        "power_input_5v": [],
                        "io_voltage": [],
                        "io_current": [],
                        "watchdog_reset": [],
                        "charging_temperature_fault": [],
                       }
        return pijuice_data


    def data2ms(self, data):
        return data["data"] / 1e3


    def get_data(self, pj, data, time_sec=time.time):
        timestamp = int(time_sec() * 1e3)
        try:
            status = pj.status.GetStatus()["data"]
            data["battery_charge"].append([pj.status.GetChargeLevel()["data"], timestamp])
            data["battery_voltage"].append([self.data2ms(pj.status.GetBatteryVoltage()), timestamp])
            data["battery_current"].append([self.data2ms(pj.status.GetBatteryCurrent()), timestamp])
            data["battery_temperature"].append([pj.status.GetBatteryTemperature()["data"], timestamp])
            data["battery_status"].append([status["battery"], timestamp])
            data["power_input"].append([status["powerInput"], timestamp])
            data["power_input_5v"].append([status["powerInput5vIo"], timestamp])
            data["io_voltage"].append([self.data2ms(pj.status.GetIoVoltage()), timestamp])
            data["io_current"].append([self.data2ms(pj.status.GetIoCurrent()), timestamp])
            faults = pj.status.GetFaultStatus()["data"]
            if "watchdog_reset" in faults:
                data["watchdog_reset"].append([faults["watchdog_reset"], timestamp])
                pj.status.ResetFaultFlags(["watchdog_reset"])
            else:
                data["watchdog_reset"].append([False, timestamp])
            if "charging_temperature_fault" in faults:
                data["charging_temperature_fault"].append([faults["charging_temperature_fault"], timestamp])
            else:
                data["charging_temperature_fault"].append([False, timestamp])
        except Exception as e:
            print(f'Failed to read PiJuice because: {e}')
        return data


    def main(self):
        import pijuice  # pylint: disable=import-error # pytype: disable=import-error

        os.makedirs(self.data_dir, exist_ok=True)

        # copy files to host that are needed for pijuice
        shutil.copyfile('/pijuice_config.JSON', '/var/lib/pijuice/pijuice_config.JSON')
        shutil.copyfile('/shutdown.sh', '/home/pi/shutdown.sh')

        # fix permissions
        os.system('chown 1000:1000 /home/pi/shutdown.sh')
        os.system('chmod +x /home/pi/shutdown.sh')

        data = self.init_data()

        while not os.path.exists('/dev/i2c-1'):
            time.sleep(0.1)

        pj = pijuice.PiJuice(1, 0x14)

        pj.config.SetBatteryProfile('PJLIPO_12000')
        pj.rtcAlarm.SetWakeupEnabled(False)
        pj.power.SetWakeUpOnCharge(10, True)
        sw = pj.power.SetWatchdog(60, True)
        print(f'SetWatchdog() returned {sw}')
        swc = pj.power.GetWatchdog()
        print(f'GetWatchdog() returned {swc}')

        write_cycles = 1
        while True:
            data = self.get_data(pj, data)
            if write_cycles == 15:  # write out every 15 minutes
                write_timestamp = int(time.time())
                self.write_data(write_timestamp, data)
                data = self.init_data()
                write_cycles = 1
            write_cycles += 1
            time.sleep(60)  # 1 minute between checks


if __name__ == '__main__':
    pw = Power()
    pw.main()
