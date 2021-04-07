#!/usr/bin/python3

"""SleepyPi hat manager."""

import argparse
import json
import time
import serial


class SerialException(Exception):
    """Serial port exception."""


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
        'timestamp': time.time(),
        'command': json.loads(command_bytes.decode()),
        'response': {},
    }
    if response_bytes:
        summary['response'] = json.loads(response_bytes.decode())
    return summary


def loop(args):
    """Event loop."""

    # TODO: sync sleepypi rtc with settime/hwclock -w if out of sync
    # TODO: thresholds/FSM for duty cycle snoozing on low battery
    while True:
        try:
            with open(args.log, 'a') as logfile:
                logfile.write(json.dumps(
                    send_command(
                        '{"command": "sensors"}',
                        args.port, args.speed, args.timeout)) + '\n')
        except SerialException:
            pass
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
    main_args = parser.parse_args()
    loop(main_args)
