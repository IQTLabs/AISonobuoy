import os

from power_app import Power

test_dir = os.path.join('.', '/tmp/aisonobuoy-test')

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
    pass


def test_main():
    pass
