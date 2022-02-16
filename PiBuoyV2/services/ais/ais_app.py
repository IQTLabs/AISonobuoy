# using pyais 1.5.0
from pyais import decode_raw

import glob
import json
import os
import serial
import socket
import time


class AIS:

    def __init__(self, data_dir='/flash/telemetry/ais', serial_impl=serial.Serial):
        self.hostname = os.getenv("HOSTNAME", socket.gethostname())
        self.data_dir = data_dir
        self.serial_impl = serial_impl

    @staticmethod
    def getAIS(aisc, results):
        data = aisc.readline()
        if data:
            try:
                msg = decode_raw(data)
                timestamp = int(time.time())
                for key in msg.keys():
                    if key in ['status', 'maneuver', 'epfd', 'shiptype', 'aid_type', 'station_type', 'ship_type', 'txrx', 'interval']:
                        msg[key] = msg[key].name
                msg['timestamp'] = timestamp
                print(f'{msg}')
                results.append(msg)
            except Exception as e:
                print(f'Bad formatted data: {data}')
        return results

    def rename_dotfiles(self):
        for dotfile in glob.glob(os.path.join(self.data_dir, '.*')):
            basename = os.path.basename(dotfile)
            non_dotfile = os.path.join(self.data_dir, basename[1:])
            os.rename(dotfile, non_dotfile)

    def main(self):
        SERIAL_PORT = "/dev/serial0"
        running = True

        print("AIS application started!")
        aisc = self.serial_impl(SERIAL_PORT, baudrate=38400, timeout=1)

        os.makedirs(self.data_dir, exist_ok=True)
        start_time = int(time.time())
        records = []
        while running:
            try:
                tmp_filename = f'{self.data_dir}/.{self.hostname}-{start_time}-ais.json'
                # check if 15 minutes have elapsed
                if int(time.time()) >= (start_time + 900):
                    self.rename_dotfiles()
                    start_time = int(time.time())
                if len(records) > 0:
                    with open(tmp_filename, 'a') as f:
                        for record in records:
                            try:
                                f.write(f'{json.dumps(record)}\n')
                            except Exception as e:
                                f.write('{"error":"'+str(record)+'"}\n')
                    records = []
                records = self.getAIS(aisc, records)
                time.sleep(1)
            except KeyboardInterrupt:
                running = False
                aisc.close()
                print("AIS application stopped!")


if __name__ == '__main__':
    a = AIS()
    a.main()
