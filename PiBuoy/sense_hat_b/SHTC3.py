#!/usr/bin/python
# -*- coding:utf-8 -*-
import ctypes
import json
import os
import socket
import time

samples = 100

class SHTC3:
    def __init__(self):
        self.dll = ctypes.CDLL("/opt/BiggerBoat/PiBuoy/sense_hat_b/SHTC3.so")
        init = self.dll.init
        init.restype = ctypes.c_int
        init.argtypes = [ctypes.c_void_p]
        init(None)

    def SHTC3_Read_Temperature(self):
        temperature = self.dll.SHTC3_Read_TH
        temperature.restype = ctypes.c_float
        temperature.argtypes = [ctypes.c_void_p]
        return temperature(None)

    def SHTC3_Read_Humidity(self):
        humidity = self.dll.SHTC3_Read_RH
        humidity.restype = ctypes.c_float
        humidity.argtypes = [ctypes.c_void_p]
        return humidity(None)


if __name__ == "__main__":
    shtc3 = SHTC3()
    sensor_data = {"humidity": [],
                   "temperature": [],
                  }
    for i in range(samples):
        time.sleep(1/samples)
        timestamp = int(time.time()*1000)
        sensor_data['temperature'].append([shtc3.SHTC3_Read_Temperature(), timestamp])
        sensor_data['humidity'].append([shtc3.SHTC3_Read_Humidity(), timestamp])

    hostname = socket.gethostname()
    timestamp = int(time.time()*1000)
    f_dir = f'/flash/telemetry/sensors'
    os.makedirs(f_dir, exist_ok=True)

    with open(f'{f_dir}/{hostname}-{timestamp}-shtc3.json', 'w') as f:
        for key in sensor_data.keys():
            record = {"target":key, "datapoints": sensor_data[key]}
            f.write(f'{json.dumps(record)}\n')
