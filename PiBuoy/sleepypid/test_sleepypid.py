#!/usr/bin/python3

import tempfile
import unittest
from collections import namedtuple
from sleepypid import get_uptime, mean_diff, sleep_duty_seconds, calc_soc, log_grafana, call_script


class SleepyidTestCase(unittest.TestCase):
    """Test sleepypid"""

    def test_call_script(self):
        call_script('ls')
        call_script('/bin/notsogood')
        call_script('cat', timeout=2)

    def test_uptime(self):
        self.assertGreaterEqual(get_uptime(), 0)

    def test_soc(self):
        args = namedtuple('args', ('fullvoltage', 'shutdownvoltage'))
        args.fullvoltage=13.3
        args.shutdownvoltage=12.9
        self.assertEqual(100, calc_soc(13.3, args))
        self.assertEqual(100, calc_soc(14, args))
        self.assertEqual(0, calc_soc(12.9, args))
        self.assertEqual(0, calc_soc(12.8, args))
        self.assertAlmostEqual(50, calc_soc(13.1, args), places=2)

    def test_log_grafana(self):
        with tempfile.TemporaryDirectory() as test_dir:
            log_grafana(True, test_dir,
                {"command": {"command": "sensors"},
                 "response": {"command": "sensors", "error": "", "rpiCurrent": 1, "supplyVoltage": 1, "mean1mSupplyVoltage": 1,
                              "mean1mRpiCurrent": 1, "min1mSupplyVoltage": 1, "min1mRpiCurrent": 1, "max1mSupplyVoltage": 1,
                              "max1mRpiCurrent": 1, "meanValid": True, "powerState": True, "powerStateOverride": False, "uptimems": 1},
                              "timestamp": 1, "utctimestamp": "2021-01-01 01:11:11.11",
                              "loadavg": [1, 1, 1], "uptime": 1, "cputempc": 5})
            log_grafana(True, test_dir,
                {"window_diffs": {"mean1mRpiCurrent": 0.1, "mean1mSupplyVoltage": -0.01, "cputempc": 0.01}, "soc": 100, "timestamp": 1,
                                  "utctimestamp": "2021-01-01 01:11:11.11", "loadavg": [1, 1, 1], "uptime": 1, "cputempc": 5})

    def test_mean_diff(self):
        self.assertEqual(0, mean_diff([0, 1, 2, 3, 4, 3, 2, 1, 0]))
        self.assertEqual(0, mean_diff([1, 1]))
        self.assertEqual(-0.25, mean_diff([1, 1.5, 0.5]))
        voltages = [12.8, 12.8, 12.8, 12.9, 12.9, 12.9, 13.0, 13.0, 13.0]
        self.assertAlmostEqual(0.025, mean_diff(voltages), places=2)
        self.assertAlmostEqual(-0.025, mean_diff(list(reversed(voltages))), places=2)

    def test_sleep_duty_seconds(self):
        self.assertEqual(0, sleep_duty_seconds(100, 15, 1440))
        self.assertEqual(1440, sleep_duty_seconds(0, 15, 1440))
        pct75_sleep_time = 0
        for _ in range(1000):
            pct75_sleep_time += sleep_duty_seconds(75, 15, 1440)
        pct50_sleep_time = 0
        for _ in range(1000):
            pct50_sleep_time += sleep_duty_seconds(50, 15, 1440)
        pct10_sleep_time = 0
        for _ in range(1000):
            pct10_sleep_time += sleep_duty_seconds(10, 15, 1440)
        self.assertGreater(pct10_sleep_time, pct50_sleep_time)
        self.assertGreater(pct50_sleep_time, pct75_sleep_time)


if __name__ == '__main__':
    unittest.main()
