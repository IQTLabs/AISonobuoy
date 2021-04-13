from gps import *

import json
import time

def collect_gpsd(session, filename):
    try:
        # Wait for messages
        report = session.next()
        print("New item collected")

        # Write messages out to line delimited json file
        with open(filename, 'a') as f:
            json.dump(dict(report), f)
            f.write("\n")

        # Clean up our current connection
        if report['class'] == 'DEVICE':
            session.close()
            session = gps(mode=WATCH_ENABLE)
    except StopIteration:
        print("GPSD has terminated")
        session = gps(mode=WATCH_ENABLE)
    return session


try:
    start_time = time.time()
    filename = "gpsd-"+str(start_time)+".json"
    session = gps(mode=WATCH_ENABLE)
    print("Connected to GPSD...")
    while True:
        new_time = time.time()
        if new_time-start_time > 900:
            filename = "gpsd-"+str(new_time)+".json"
        try:
            session = collect_gpsd(session, filename)
        except Exception as e:
            print("Retrying...")
            session = gps(mode=WATCH_ENABLE)
except Exception as e:
    print("Unable to connect to GPSD")
