import os

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


class FakePJ:

    def __init__(self):
        self.status = FakePJStatus()


def test_rename_dotfiles():
    pw = Power()
    os.makedirs(test_dir, exist_ok=True)
    pw.data_dir = test_dir
    pw.rename_dotfiles()


def test_write_data():
    pw = Power()
    os.makedirs(test_dir, exist_ok=True)
    pw.data_dir = test_dir
    pw.write_data(1234, {'foo': 'bar'})


def test_init_data():
    pw = Power()
    data = pw.init_data()
    assert isinstance(data, dict)


def test_get_data():
    pw = Power()
    data = pw.init_data()
    def time_sec():
        return 1
    ret = pw.get_data(FakePJ(), data, time_sec=time_sec)
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
    pass
