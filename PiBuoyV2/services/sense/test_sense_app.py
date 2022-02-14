from sense_app import Telemetry  # pylint: disable=no-name-in-module
from hooks import get_url, message_card_template, insert_message_data, send_hook


def test_telemetry():

    class MockEvent:

        def __init__(self):
            self.action = 'released'
            self.direction = 'middle'


    class MockStick:

        def get_events(self):
            return [MockEvent()]


    class MockSense:

        def __init__(self):
            self.stick = MockStick()

        def get_temperature(self):
            return 10

        def get_humidity(self):
            return 10

        def get_pressure(self):
            return 10

        def get_accelerometer_raw(self):
            return {'x': 10, 'y': 10, 'z': 10}

        def get_gyroscope_raw(self):
            return {'x': 10, 'y': 10, 'z': 10}

        def get_compass_raw(self):
            return {'x': 10, 'y': 10, 'z': 10}

        def set_pixel(self, x, y, color):
            pass

        def set_pixels(self, matrix):
            pass


    t = Telemetry('.')
    t.sense = MockSense()
    t.MINUTES_BETWEEN_WAKES = 1.1
    t.MINUTES_BETWEEN_WRITES = 2
    t.main(False)


def test_reorder_dots():
    files = ['.asdf', '.qwer', 'foo', 'bar']
    files = Telemetry().reorder_dots(files)
    assert files == ['foo', 'bar', '.asdf', '.qwer']


def test_get_url():
    url = get_url()
    assert url == ""


def test_message_card_template():
    card = message_card_template()
    assert isinstance(card, dict)


def test_insert_message_data():
    data = {}
    data['title'] = 'foo'
    data['themeColor'] = 'foo'
    data['body_title'] = 'foo'
    data['body_subtitle'] = 'foo'
    data['text'] = 'foo'
    data['facts'] = [{'foo':'bar'}]
    card = insert_message_data(data)
    assert card['title'] == 'foo'
    assert card['themeColor'] == 'foo'
    assert card['sections'][0]['activityTitle'] == 'foo'
    assert card['sections'][0]['activitySubtitle'] == 'foo'
    assert card['sections'][0]['text'] == 'foo'
    assert card['sections'][0]['facts'] == [{'foo':'bar'}]


def test_send_hook():
    response = send_hook(message_card_template())
