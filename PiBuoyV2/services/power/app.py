import glob
import json
import os
import socket
import time

import pijuice  # pylint: disable=import-error # pytype: disable=import-error

def rename_dotfiles(flashdir):
    for dotfile in glob.glob(os.path.join(flashdir, '.*')):
        basename = os.path.basename(dotfile)
        non_dotfile = os.path.join(flashdir, basename[1:])
        os.rename(dotfile, non_dotfile)


def write_data(hostname, timestamp, data_dir, data):
    tmp_filename = f'{data_dir}/.{hostname}-{timestamp}-power.json'
    with open(tmp_filename, 'a') as f:
        for key in data.keys():
            record = {"target":key, "datapoints": data[key]}
            f.write(f'{json.dumps(record)}\n')
    rename_dotfiles(data_dir)


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


def get_data(pj, data):
    try:
        timestamp = int(time.time()*1000)
        status = pj.status.GetStatus()["data"]
        data["battery_charge"].append([pj.status.GetChargeLevel()["data"], timestamp])
        data["battery_voltage"].append([pj.status.GetBatteryVoltage()["data"] / 1000, timestamp])
        data["battery_current"].append([pj.status.GetBatteryCurrent()["data"] / 1000, timestamp])
        data["battery_temperature"].append([pj.status.GetBatteryTemperature()["data"], timestamp])
        data["battery_status"].append([status["battery"], timestamp])
        data["power_input"].append([status["powerInput"], timestamp])
        data["power_input_5v"].append([status["powerInput5vIo"], timestamp])
        data["io_voltage"].append([pj.status.GetIoVoltage()["data"] / 1000, timestamp])
        data["io_current"].append([pj.status.GetIoCurrent()["data"] / 1000, timestamp])
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


def main():
    hostname = os.getenv("HOSTNAME", socket.gethostname())
    data_dir = '/flash/telemetry/power'
    os.makedirs(data_dir, exist_ok=True)
    data = init_data()

    while not os.path.exists('/dev/i2c-1'):
        time.sleep(0.1)

    pj = pijuice.PiJuice(1, 0x14)

    # TODO set config for wakeup/shutdown
    pj.config.SetBatteryProfile('PJLIPO_12000')
    pj.rtcAlarm.SetWakeupEnabled(True)

    write_cycles = 1
    while True:
        data = get_data(pj, data)
        if write_cycles == 15:  # write out every 15 minutes
            write_timestamp = int(time.time())
            write_data(hostname, write_timestamp, data_dir, data)
            data = init_data()
            write_cycles = 1
        write_cycles += 1
        time.sleep(60)  # 1 minute between checks


main()
