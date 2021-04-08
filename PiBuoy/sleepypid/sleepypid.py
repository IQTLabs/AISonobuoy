#!/usr/bin/python3

"""SleepyPi hat manager."""

import argparse
import json
import statistics
import time
import os
from collections import defaultdict
import serial


class SerialException(Exception):
    """Serial port exception."""


def get_temp():
    """Return CPU temperature."""
    return float(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1e3


def get_uptime():
    """Return uptime in seconds."""
    return float(open('/proc/uptime').read().split()[0])


def mean_diff(stats):
    """Return mean, of the consecutive difference of list of numbers."""
    return statistics.mean([x - y for x, y in zip(stats, stats[1:])])


def send_command(command, port, baudrate, timeout):
    """Send a JSON command to the SleepyPi hat and parse response."""

    try:
        pserial = serial.Serial(
            port=port, baudrate=baudrate, timeout=timeout, write_timeout=timeout)
        command_bytes = ('%s\r' % command).encode()
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
    return summary


def log_json(log, obj):
    """Log JSON object."""
    with open(log, 'a') as logfile:
        obj.update({
            'timestamp': time.time(),
            'loadavg': os.getloadavg(),
            'uptime': get_uptime(),
            'cputempc': get_temp(),
        })
        logfile.write(json.dumps(obj) + '\n')


def loop(args):
    """Event loop."""

    sample_count = 0
    window_stats = defaultdict(list)
    window_diffs = {}

    # TODO: sync sleepypi rtc with settime/hwclock -w if out of sync
    # TODO: thresholds/FSM for duty cycle snoozing on low battery
    while True:
        summary = None
        try:
            summary = send_command(
                '{"command": "sensors"}',
                args.port, args.speed, args.timeout)
            log_json(args.log, summary)
        except SerialException:
            pass
        if summary:
            response = summary['response']
            for stat in ('mean1mRpiCurrent', 'mean1mSupplyVoltage'):
                window_stats[stat].append(response[stat])
            for stat in ('cputempc',):
                window_stats[stat].append(summary[stat])
            sample_count += 1
            for stat in window_stats:
                window_stats[stat] = window_stats[stat][-args.window_samples:]
                if len(window_stats[stat]) > 1:
                    window_diffs[stat] = mean_diff(window_stats[stat])
            if window_diffs and sample_count >= args.window_samples:
                window_summary = {
                    'window_diffs': window_diffs,
                }
                log_json(args.log, window_summary)
        time.sleep(args.polltime)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='sleepypi hat manager')
    parser.add_argument(
        '--port', default='/dev/ttyAMA1', help='sleepypi serial port')
    parser.add_argument(
        '--speed', default=9600, type=int, help='sleepypi baudrate')
    parser.add_argument(
        '--timeout', default=5, type=int, help='sleepypi serial timeout')
    parser.add_argument(
        '--polltime', default=60, type=int, help='sleepypi sensor poll period')
    parser.add_argument(
        '--log', default='/var/log/sleepypid.log', help='sleepypi serial port')
    parser.add_argument(
        '--window_samples', default=15, type=int, help='window size for sample results')
    main_args = parser.parse_args()
    loop(main_args)
