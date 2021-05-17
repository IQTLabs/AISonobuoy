#!/usr/bin/python3

"""SleepyPi hat manager."""

import argparse
import copy
import datetime
import json
import platform
import random
import socket
import statistics
import subprocess
import sys
import time
import os
from collections import defaultdict
import serial

MIN_SLEEP_MINS = 15
MAX_SLEEP_MINS = (24 * 60) - MIN_SLEEP_MINS
MEAN_V = 'mean1mSupplyVoltage'
MEAN_C = 'mean1mRpiCurrent'
SHUTDOWN_TIMEOUT = 60
sensor_data = {}


class SerialException(Exception):
    """Serial port exception."""


def get_temp():
    """Return CPU temperature."""
    return float(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1e3


def get_uptime():
    """Return uptime in seconds."""
    with open('/proc/uptime') as uptime:
        return float(uptime.read().split()[0])


def mean_diff(stats):
    """Return mean, of the consecutive difference of list of numbers."""
    return statistics.mean([y - x for x, y in zip(stats, stats[1:])])


def sleep_duty_seconds(duty_cycle, sleep_interval_mins, max_sleep_mins):
    """Calculate sleep period if any based on duty cycle."""
    if duty_cycle >= 100:
        return 0
    if duty_cycle <= 0:
        return max_sleep_mins
    i = 0
    while random.random() * 100 >= duty_cycle:
        i += 1
    return i * sleep_interval_mins


def send_command(command, args):
    """Send a JSON command to the SleepyPi hat and parse response."""

    command_error = None

    try:
        pserial = serial.Serial(
            port=args.port, baudrate=args.speed,
            timeout=args.timeout, write_timeout=args.timeout)
        command_bytes = ('%s\r' % json.dumps(command)).encode()
        pserial.write(command_bytes)
        response_bytes = b''
        while True:
            serial_byte = pserial.read()
            if len(serial_byte) == 0 or serial_byte in (b'\r', 'b\n'):
                break
            response_bytes += serial_byte
    except serial.serialutil.SerialException as err:
        raise SerialException from err
    summary = {
        'command': json.loads(command_bytes.decode()),
        'response': {},
    }
    if response_bytes:
        summary['response'] = json.loads(response_bytes.decode())
        command_error = summary['response'].get('error', None)

    log_json(args.log, args.grafana, args.grafana_path, summary)
    return (summary, command_error)


def configure_sleepypi(args):
    """Set SleepyPi's firmware defaults."""
    summary, command_error  = send_command({'command': 'getconfig'}, args)
    response = summary.get('response', '')
    if command_error or command_error is None:
        print('getconfig failed')
        sys.exit(-1)

    pid_config = {
        'shutdownVoltage': args.deepsleepvoltage,
        'startupVoltage': args.shutdownvoltage,
        'snoozeTimeout': SHUTDOWN_TIMEOUT * 2,
        'overrideEnabled': args.overrideenabled,
    }
    pi_config = {
        'shutdownVoltage': response['shutdownVoltage'],
        'startupVoltage': response['startupVoltage'],
        'snoozeTimeout': response['snoozeTimeout'],
        'overrideEnabled': response['overrideEnabled'],
    }

    if pid_config != pi_config:
        pid_config.update({'command': 'setconfig'})
        response, command_error = send_command(pid_config, args)
        if command_error or command_error is None:
            print('setconfig failed')
            sys.exit(-1)


def log_grafana(grafana, grafana_path, obj, write_results):
    """Log grafana telemetry."""
    global sensor_data

    if not grafana:
        return
    grafana_obj = copy.copy(obj)
    timestamp = int(time.time()*1000)
    if "loadavg" in grafana_obj:
        loadavg = grafana_obj["loadavg"]
        del grafana_obj["loadavg"]
        m1, m5, m15 = loadavg
        grafana_obj["loadavg1m"] = m1
        grafana_obj["loadavg5m"] = m5
        grafana_obj["loadavg15m"] = m15
    if ("response" in grafana_obj and
            "command" in grafana_obj["response"] and
            grafana_obj["response"]["command"] == "sensors"):
        for key in grafana_obj["response"]:
            grafana_obj[key] = grafana_obj["response"][key]
        del grafana_obj["response"]
    if "window_diffs" in grafana_obj:
        for key in grafana_obj["window_diffs"]:
            grafana_obj[key+"_window_diffs"] = grafana_obj["window_diffs"][key]
        del grafana_obj["window_diffs"]
    for key in grafana_obj.keys():
        if key in sensor_data:
            sensor_data[key].append([grafana_obj[key], timestamp])
        else:
            sensor_data[key] = [[grafana_obj[key], timestamp]]
    if write_results:
        hostname = socket.gethostname()
        os.makedirs(grafana_path, exist_ok=True)
        with open(f'{grafana_path}/{hostname}-{timestamp}-sleepypi.json', 'w') as f:
            for key in sensor_data.keys():
                record = {"target":key, "datapoints": sensor_data[key]}
                f.write(f'{json.dumps(record)}\n')
        sensor_data = {}


def log_json(log, grafana, grafana_path, obj, rollover=900, iterations=0):
    """Log JSON object."""

    if os.path.isdir(log):
        ns_time = int(time.time_ns() / 1e6)
        log_dir = os.path.join(log, '%s-%u' % (platform.node(), ns_time))
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        log_path = os.path.join(log_dir, 'sleepypi.%u' % ns_time)
    else:
        log_path = log

    obj.update({
        'timestamp': time.time(),
        'utctimestamp': str(datetime.datetime.utcnow()),
        'loadavg': os.getloadavg(),
        'uptime': get_uptime(),
        'cputempc': get_temp(),
    })
    with open(log_path, 'a') as logfile:
        logfile.write(json.dumps(obj) + '\n')

    write_results = False
    if iterations != 0 and iterations % rollover == 0:
        write_results = True
    log_grafana(grafana, grafana_path, obj, write_results)


def calc_soc(mean_v, args):
    """Calculate battery SOC."""
    # TODO: consider discharge current.
    if mean_v >= args.fullvoltage:
        return 100
    if mean_v <= args.shutdownvoltage:
        return 0
    return (mean_v - args.shutdownvoltage) / (args.fullvoltage - args.shutdownvoltage) * 100


def call_script(script, timeout=SHUTDOWN_TIMEOUT):
    """Call an external script with a timeout."""
    return subprocess.call(['timeout', str(timeout), script])


def loop(args):
    """Event loop."""

    sample_count = 0
    window_stats = defaultdict(list)
    window_diffs = {}
    ticker = 0

    # TODO: sync sleepypi rtc with settime/hwclock -w if out of sync
    while True:
        summary = None
        try:
            summary, command_error = send_command({'command': 'sensors'}, args)
        except SerialException:
            pass
        if summary and not command_error:
            response = summary.get('response', None)
            if response:
                sample_count += 1
                for stat in (MEAN_C, MEAN_V):
                    window_stats[stat].append(response[stat])
                for stat in ('cputempc',):
                    window_stats[stat].append(summary[stat])
                for stat in window_stats:
                    window_stats[stat] = window_stats[stat][-(args.window_samples):]
                    if len(window_stats[stat]) > 1:
                        window_diffs[stat] = mean_diff(window_stats[stat])
                if window_diffs and sample_count >= args.window_samples:
                    soc = calc_soc(response[MEAN_V], args)
                    window_summary = {
                        'window_diffs': window_diffs,
                        'soc': soc,
                    }
                    log_json(args.log, args.grafana, args.grafana_path, window_summary, args.window_samples*60, args.polltime*ticker)

                    if args.sleepscript and (sample_count % args.window_samples == 0):
                        duration = sleep_duty_seconds(soc, MIN_SLEEP_MINS, MAX_SLEEP_MINS)
                        if duration:
                            send_command({'command': 'snooze', 'duration': duration}, args)
                            call_script(args.sleepscript)
                            sys.exit(0)

        ticker += 1
        time.sleep(args.polltime)


if __name__ == '__main__':
    DEFAULT_POLL_TIME = int(60)
    DEFAULT_WINDOW_SAMPLES = int(15 * DEFAULT_POLL_TIME / 60) # 15m
    parser = argparse.ArgumentParser(description='sleepypi hat manager')
    parser.add_argument(
        '--port', default='/dev/ttyAMA1',
        help='sleepypi serial port')
    parser.add_argument(
        '--speed', default=9600, type=int,
        help='sleepypi baudrate')
    parser.add_argument(
        '--timeout', default=5, type=int,
        help='sleepypi serial timeout')
    parser.add_argument(
        '--polltime', default=DEFAULT_POLL_TIME, type=int,
        help='sleepypi sensor poll period')
    parser.add_argument(
        '--log', default='/var/log/sleepypid.log',
        help='if a file, log to this file, if a directory, log telemetry in a subdirectory')
    parser.add_argument(
        '--window_samples', default=DEFAULT_WINDOW_SAMPLES, type=int,
        help='window size for sample results')
    parser.add_argument(
        '--deepsleepvoltage', default=12.8, type=float,
        help='voltage at which sleepypi will disable power itself')
    parser.add_argument(
        '--shutdownvoltage', default=12.9, type=float,
        help='voltage at which sleepyid will disable power')
    parser.add_argument(
        '--fullvoltage', default=13.3, type=float,
        help='voltage at which the battery is considered full')
    parser.add_argument(
        '--overrideenabled', default=1, type=int,
        help='enable the sleepypi power override button')
    parser.add_argument('--sleepscript', default='',
        help='script to run to clean poweroff')
    parser.add_argument('--startscript', default='',
        help='script to run on startup')
    parser.add_argument(
        '--grafana-path', default='/telemetry/sensors',
        help='directory to write out JSON files for Grafana, only enabled if Grafana is enabled')
    parser.add_argument('--grafana', dest='grafana', action='store_true')
    parser.add_argument('--no-grafana', dest='grafana', action='store_false')
    parser.set_defaults(grafana=True)
    main_args = parser.parse_args()
    assert main_args.shutdownvoltage > main_args.deepsleepvoltage
    assert main_args.fullvoltage > main_args.shutdownvoltage
    if main_args.startscript:
        call_script(main_args.startscript)
    configure_sleepypi(main_args)
    loop(main_args)
