from pyais import decode_raw

import serial
import time

SERIAL_PORT = "/dev/serial0"
running = True

print("Application started!")
aisc = serial.Serial(SERIAL_PORT, baudrate=38400, timeout=1)

def getAIS(aisc):
    data = aisc.readline()
    if data:
        print(data)
        msg = decode_raw(data)
        print(msg)

while running:
    try:
        getAIS(aisc)
        time.sleep(1)
    except KeyboardInterrupt:
        running = False
        aisc.close()
        print("Application stopped!")
    except Exception as e:
        print(f"Application error: {e}")
