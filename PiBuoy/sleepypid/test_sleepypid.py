#!/usr/bin/python3

import unittest
from collections import namedtuple
from sleepypid import get_uptime, mean_diff, sleep_duty_seconds, calc_soc


class SleepyidTestCase(unittest.TestCase):
    """Test sleepypid"""

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
        for i in range(1000):
            pct75_sleep_time += sleep_duty_seconds(75, 15, 1440)
        pct50_sleep_time = 0
        for i in range(1000):
            pct50_sleep_time += sleep_duty_seconds(50, 15, 1440)
        pct10_sleep_time = 0
        for i in range(1000):
            pct10_sleep_time += sleep_duty_seconds(10, 15, 1440)
        self.assertGreater(pct10_sleep_time, pct50_sleep_time)
        self.assertGreater(pct50_sleep_time, pct75_sleep_time)


if __name__ == '__main__':
    unittest.main()
