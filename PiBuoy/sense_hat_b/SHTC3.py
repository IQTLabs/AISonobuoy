#!/usr/bin/python
# -*- coding:utf-8 -*-
import ctypes
import time

samples = 100

class SHTC3:
    def __init__(self):
        self.dll = ctypes.CDLL("./SHTC3.so")
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
    start_time = time.time()
    temp = []
    humidity = []
    for i in range(samples):
        temp.append(shtc3.SHTC3_Read_Temperature())
        humidity.append(shtc3.SHTC3_Read_Humidity())
    records = {"start_time": start_time,
               "end_time": time.time(),
               "temperature": temp,
               "humidity": humidity,
              }
    # TODO do something with records
    print(records)
