import json
import glob
import os
import tempfile
from power_app import Power

test_dir = os.path.join('.', '/tmp/aisonobuoy-test')


class FakePJStatus:

    def __init__(self):
        return

    def _retdata(self, data):
        return {'data': data}

    def GetChargeLevel(self):
        return self._retdata(0)

    def GetBatteryVoltage(self):
        return self._retdata(9)

    def GetBatteryCurrent(self):
        return self._retdata(10)

    def GetBatteryTemperature(self):
        return self._retdata(11)

    def GetIoCurrent(self):
        return self._retdata(12)

    def GetIoVoltage(self):
        return self._retdata(12)

    def GetStatus(self):
        return self._retdata({
            'battery': 1,
            'powerInput': 1,
            'powerInput5vIo': 1,
        })

    def GetFaults(self):
        return self._retdata({
            'watchdog_reset': 1,
            'charging_temperature_fault': 1,
        })

    def GetFaultStatus(self):
        return self._retdata({
            'watchdog_reset': 2,
            'charging_temperature_fault': 2,
        })

    def ResetFaultFlags(self, _faults):
        return


class FakePJConfig:

    def __init__(self):
        return

    def SetBatteryProfile(self, _profile):
        return


class FakePJRtc:

    def __init__(self):
        return

    def SetWakeupEnabled(self, alarm):
        return


class FakePJPower:

    def __init__(self):
        return

    def SetWakeUpOnCharge(self, _a, _b):
        return

    def SetWatchdog(self, _a, _b):
        return

    def GetWatchdog(self):
        return None


class FakePJ:

    def __init__(self):
        self.status = FakePJStatus()
        self.config = FakePJConfig()
        self.rtcAlarm = FakePJRtc()
        self.power = FakePJPower()


class FakePJLib:

    def PiJuice(self, _a, _b):
        return FakePJ()


def fakepj_factory():
    return FakePJLib()


def time_sec():
    return 1


def test_rename_dotfiles():
    with tempfile.TemporaryDirectory() as tmpdir:
        pw = Power(root_dir=tmpdir, time_sec=time_sec)
        pw.rename_dotfiles()


def test_write_data():
    with tempfile.TemporaryDirectory() as tmpdir:
        pw = Power(root_dir=tmpdir, data_dir='./', time_sec=time_sec)
        pw.write_data({'foo': 'bar'})


def test_init_data():
    with tempfile.TemporaryDirectory() as tmpdir:
        pw = Power(root_dir=tmpdir, time_sec=time_sec)
        data = pw.init_data()
        assert isinstance(data, dict)


def test_get_data():
    with tempfile.TemporaryDirectory() as tmpdir:
        pw = Power(root_dir=tmpdir, time_sec=time_sec)
        data = pw.init_data()
        ret = pw.get_data(FakePJ(), data)
        assert ret == {
            'battery_charge': [[0, 1000]],
            'battery_voltage': [[0.009, 1000]],
            'battery_current': [[0.01, 1000]],
            'battery_temperature': [[11, 1000]],
            'battery_status': [[1, 1000]],
            'power_input': [[1, 1000]],
            'power_input_5v': [[1, 1000]],
            'io_voltage': [[0.012, 1000]],
            'io_current': [[0.012, 1000]],
            'watchdog_reset': [[2, 1000]],
            'charging_temperature_fault': [[2, 1000]]
        }


def test_main():
    with tempfile.TemporaryDirectory() as tmpdir:
        pw = Power(root_dir=tmpdir, time_sec=time_sec, uid=os.getuid(), gid=os.getgid())
        for test_dir in ('dev/i2c-1', 'var/lib/pijuice', 'home/pi'):
            os.makedirs(os.path.join(tmpdir, test_dir), exist_ok=True)
        for test_file in ('pijuice_config.JSON', 'shutdown.sh'):
            with open(os.path.join(tmpdir, test_file), 'w') as f:
                f.write('test')
        def poll_wait():
            raise KeyboardInterrupt
        pw.main(get_pijuice=fakepj_factory, poll_wait=poll_wait)
        results = glob.glob(os.path.join(pw.data_dir, '*json'))
        assert len(results) == 1
        with open(results[0]) as f:
            json_results = [json.loads(line.strip()) for line in f.readlines()]
            assert json_results == [
                {'target': 'battery_charge', 'datapoints': [[0, 1000]]},
                {'target': 'battery_voltage', 'datapoints': [[0.009, 1000]]},
                {'target': 'battery_current', 'datapoints': [[0.01, 1000]]},
                {'target': 'battery_temperature', 'datapoints': [[11, 1000]]},
                {'target': 'battery_status', 'datapoints': [[1, 1000]]},
                {'target': 'power_input', 'datapoints': [[1, 1000]]},
                {'target': 'power_input_5v', 'datapoints': [[1, 1000]]},
                {'target': 'io_voltage', 'datapoints': [[0.012, 1000]]},
                {'target': 'io_current', 'datapoints': [[0.012, 1000]]},
                {'target': 'watchdog_reset', 'datapoints': [[2, 1000]]},
                {'target': 'charging_temperature_fault', 'datapoints': [[2, 1000]]}]
