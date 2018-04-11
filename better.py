import json
import sys
from time import time
from datetime import datetime

import requests
import mongoengine as me


class Package(me.Document):
    name = me.StringField()
    latest_version = me.StringField()
    last_check = me.StringField()


def time_to_date(timestamp, datetime=datetime):
    return datetime.fromtimestamp(timestamp).ctime()


def fetch_package_version(pkg_name):
    response = requests.get(f'http://pypi.python.org/pypi/{pkg_name}/json')

    if response.status_code == 200:
        version = response.json()['info']['version']
        return version, int(time())
    else:
        raise Exception(
            f'failed to fetch {pkg_name} latest version: {response.text}')


def create_package(name, version, last_check):
    package = Package()
    package.name = name
    package.latest_version = version
    package.last_check = last_check
    print(package.to_json())
    package.save()


def save_last_check(name, version, last_check):
    with open('last_check.csv', 'w') as f:
        f.write(f'{name},{version},{last_check}')


def run(config, pkg_name):
    db_conf = {
        'db': config['MONGO_DB_NAME'],
        'host': config['MONGO_URL']
    }
    me.connect(**db_conf)

    try:
        version, timestamp = fetch_package_version(pkg_name)
        last_check = time_to_date(timestamp)
        create_package(pkg_name, version, last_check)
        save_last_check(pkg_name, version, last_check)

    except Exception as err:
        print(str(err))


if __name__ == '__main__':
    config = {'MONGO_DB_NAME': 'pkg_info', 'MONGO_URL': 'localhost:27017'}
    run(config, sys.argv[1])
