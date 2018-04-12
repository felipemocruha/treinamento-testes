import json
from requests import Response
from nose.tools import assert_raises
from mock import MagicMock

from pkg_version.even_better import *


def test_time_to_date():
    now = 1523556663
    expected = 'Thu Apr 12 15:11:03 2018'

    assert time_to_date(now) == expected


def test_time_to_date_str():
    now = '1523556663'
    expected = 'Thu Apr 12 15:11:03 2018'

    with assert_raises(TypeError):
        time_to_date(now)


class FakePackage(object):
    def __init__(self):
        self.name = None
        self.latest_version = None
        self.last_check = None

    def save(self):
        pass

    def to_json(self):
        pkg = {
            'name': self.name,
            'latest_version': self.latest_version,
            'last_check': self.last_check
        }
        return json.dumps(pkg)


def test_create_package():
    entry = ['numpy', '1.0.0', 'Thu Apr 12 15:11:03 2018']

    pkg = create_package(*entry, Package=FakePackage)
    assert pkg.name == entry[0]
    assert pkg.latest_version == entry[1]
    assert pkg.last_check == entry[2]


def test_fetch():
    resp = Response()
    resp.status_code = 200
    resp._content = b'{"info": {"version": "1.0.0"}}'

    now = 1523556663
    request = MagicMock()
    request.get.return_value = resp
    times = lambda: now

    v, t = fetch_package_version('numpy',
                                 requests=request,
                                 time=times)
    assert v == '1.0.0'
    assert t == now


def test_fetch_fail():
    resp = Response()
    resp.status_code = 404
    resp._content = b'Not found'

    request = MagicMock()
    request.get.return_value = resp

    with assert_raises(Exception):
       fetch_package_version('numpy',
                             requests=request)
