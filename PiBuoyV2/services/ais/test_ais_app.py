import json
import glob
import os
import tempfile
from ais_app import AIS


class FakeSerial:

    def __init__(self, serial_port, baudrate, timeout):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.message = "!AIVDM,1,1,,A,403Ovl@000Htt<tSF0l4Q@100`Pq,0*28\n"

    def readline(self):
        if self.message:
            ret = self.message
            self.message = None
            return ret
        raise KeyboardInterrupt

    def close(self):
        return


def test_main():
    with tempfile.TemporaryDirectory() as tmpdir:
        a = AIS(data_dir=tmpdir, serial_impl=FakeSerial)
        a.main()
        a.rename_dotfiles()
        json_files = glob.glob(os.path.join(tmpdir, '*json'))
        assert len(json_files) == 1
        with open(json_files[0]) as f:
            record = json.load(f)
        del record['timestamp']
        assert record == {
                'type': 4, 'repeat': 0, 'mmsi': '003669713', 'year': 0, 'month': 0, 'day': 0, 'hour': 24, 'minute': 60, 'second': 60,
                'accuracy': 0, 'lon': 181.0, 'lat': 91.0, 'epfd': 'GPS', 'raim': 0, 'radio': 165945}
