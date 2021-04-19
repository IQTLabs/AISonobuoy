from gps import *

import json
import time


try:
    start_time = time.time()
    filename = "gpsd-"+str(start_time)+".json"
    session = gps(mode=WATCH_ENABLE)
    print("Connected to GPSD...")
    while True:
        new_time = time.time()
        if new_time-start_time > 900:
            filename = "gpsd-"+str(new_time)+".json"
        # Wait for messages
        report = session.next()
        print("New item collected")

        # Write messages out to line delimited json file
        with open(filename, 'a') as f:
            try:
                json.dump(dict(report), f)
                f.write("\n")
            except Exception as e:
                print(f'Unable to write: {report} because: {e}')
except Exception as e:
    print("Unable to connect to GPSD")
