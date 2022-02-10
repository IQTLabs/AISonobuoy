from sense_app import Telemetry  # pylint: disable=no-name-in-module
from hooks import get_url, message_card_template, insert_message_data, send_hook


def test_telemetry():
    t = Telemetry()


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
    assert card['sections'][0]['activitySubbtitle'] == 'foo'
    assert card['sections'][0]['text'] == 'foo'
    assert card['sections'][0]['facts'] == [{'foo':'bar'}]


def test_send_hook():
    response = send_hook(message_card_template())
