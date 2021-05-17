from pyais import decode_raw

import json
import os
import serial
import socket
import time

SERIAL_PORT = "/dev/serial0"
running = True

print("Application started!")
aisc = serial.Serial(SERIAL_PORT, baudrate=38400, timeout=1)


def getAIS(aisc, f_dir, hostname):
    data = aisc.readline()
    if data:
        print(data)
        try:
            msg = decode_raw(data)
            print(msg)
            timestamp = int(time.time()*1000)
            with open(f'{f_dir}/{hostname}-{timestamp}-ais.json', 'w') as f:
                json.dump(msg, f)
                f.write("\n")
        except Exception as e:
            print(f'Bad formatted data: {data}')

while running:
    hostname = socket.gethostname()
    f_dir = f'/telemetry/ais'
    os.makedirs(f_dir, exist_ok=True)
    try:
        getAIS(aisc, f_dir, hostname)
        time.sleep(1)
    except KeyboardInterrupt:
        running = False
        aisc.close()
        print("Application stopped!")
    except Exception as e:
        print(f"Application error: {e}")
