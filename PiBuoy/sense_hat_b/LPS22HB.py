#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import os
import smbus
import socket
import time

samples = 100

#i2c address
LPS22HB_I2C_ADDRESS   =  0x5C
#
LPS_ID                =  0xB1
#Register
LPS_INT_CFG           =  0x0B        #Interrupt register
LPS_THS_P_L           =  0x0C        #Pressure threshold registers
LPS_THS_P_H           =  0x0D
LPS_WHO_AM_I          =  0x0F        #Who am I
LPS_CTRL_REG1         =  0x10        #Control registers
LPS_CTRL_REG2         =  0x11
LPS_CTRL_REG3         =  0x12
LPS_FIFO_CTRL         =  0x14        #FIFO configuration register
LPS_REF_P_XL          =  0x15        #Reference pressure registers
LPS_REF_P_L           =  0x16
LPS_REF_P_H           =  0x17
LPS_RPDS_L            =  0x18        #Pressure offset registers
LPS_RPDS_H            =  0x19
LPS_RES_CONF          =  0x1A        #Resolution register
LPS_INT_SOURCE        =  0x25        #Interrupt register
LPS_FIFO_STATUS       =  0x26        #FIFO status register
LPS_STATUS            =  0x27        #Status register
LPS_PRESS_OUT_XL      =  0x28        #Pressure output registers
LPS_PRESS_OUT_L       =  0x29
LPS_PRESS_OUT_H       =  0x2A
LPS_TEMP_OUT_L        =  0x2B        #Temperature output registers
LPS_TEMP_OUT_H        =  0x2C
LPS_RES               =  0x33        #Filter reset register

class LPS22HB(object):
    def __init__(self,address=LPS22HB_I2C_ADDRESS):
        self._address = address
        self._bus = smbus.SMBus(1)
        self.LPS22HB_RESET()                         #Wait for reset to complete
        self._write_byte(LPS_CTRL_REG1 ,0x02)        #Low-pass filter disabled , output registers not updated until MSB and LSB have been read , Enable Block Data Update , Set Output Data Rate to 0

    def LPS22HB_RESET(self):
        Buf=self._read_u16(LPS_CTRL_REG2)
        Buf|=0x04
        self._write_byte(LPS_CTRL_REG2,Buf)               #SWRESET Set 1
        while Buf:
            Buf=self._read_u16(LPS_CTRL_REG2)
            Buf&=0x04

    def LPS22HB_START_ONESHOT(self):
        Buf=self._read_u16(LPS_CTRL_REG2)
        Buf|=0x01                                         #ONE_SHOT Set 1
        self._write_byte(LPS_CTRL_REG2,Buf)

    def _read_byte(self,cmd):
        return self._bus.read_byte_data(self._address,cmd)

    def _read_u16(self,cmd):
        LSB = self._bus.read_byte_data(self._address,cmd)
        MSB = self._bus.read_byte_data(self._address,cmd+1)
        return (MSB << 8) + LSB

    def _write_byte(self,cmd,val):
        self._bus.write_byte_data(self._address,cmd,val)

if __name__ == '__main__':
    PRESS_DATA = 0.0
    TEMP_DATA = 0.0
    u8Buf=[0,0,0]
    lps22hb=LPS22HB()
    sensor_data = {"pressure": [],
                   "temperature": [],
                  }
    for i in range(samples):
        time.sleep(1/samples)
        timestamp = int(time.time()*1000)
        lps22hb.LPS22HB_START_ONESHOT()
        if (lps22hb._read_byte(LPS_STATUS)&0x01)==0x01:  # a new pressure data is generated
            u8Buf[0]=lps22hb._read_byte(LPS_PRESS_OUT_XL)
            u8Buf[1]=lps22hb._read_byte(LPS_PRESS_OUT_L)
            u8Buf[2]=lps22hb._read_byte(LPS_PRESS_OUT_H)
            PRESS_DATA=((u8Buf[2]<<16)+(u8Buf[1]<<8)+u8Buf[0])/4096.0
        if (lps22hb._read_byte(LPS_STATUS)&0x02)==0x02:   # a new pressure data is generated
            u8Buf[0]=lps22hb._read_byte(LPS_TEMP_OUT_L)
            u8Buf[1]=lps22hb._read_byte(LPS_TEMP_OUT_H)
            TEMP_DATA=((u8Buf[1]<<8)+u8Buf[0])/100.0

        sensor_data['pressure'].append([PRESS_DATA, timestamp])
        sensor_data['pressure_temperature'].append([TEMP_DATA, timestamp])

    hostname = socket.gethostname()
    timestamp = int(time.time()*1000)
    f_dir = f'/telemetry/sensors'
    os.makedirs(f_dir, exist_ok=True)

    with open(f'{f_dir}/{hostname}-{timestamp}-lps22hb.json', 'w') as f:
        for key in sensor_data.keys():
            record = {"target":key, "datapoints": sensor_data[key]}
            f.write(f'{json.dumps(record)}\n')
