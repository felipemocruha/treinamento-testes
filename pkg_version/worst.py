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


def fetch_package_version(config):
    pkg_name = sys.argv[1]

    db_conf = {
        'db': config['MONGO_DB_NAME'],
        'host': config['MONGO_URL']
    }
    me.connect(**db_conf)

    response = requests.get(f'http://pypi.python.org/pypi/{pkg_name}/json')

    if response.status_code == 200:
        version = response.json()['info']['version']
        package = Package()
        package.name = pkg_name
        package.latest_version = version
        package.last_check = datetime.fromtimestamp(int(time())).ctime()
        print(package.to_json())
        package.save()

        with open('last_check.csv', 'w') as f:
            f.write(f'{package.name},{package.latest_version},{package.last_check}')

    else:
        print(f'failed to fetch {pkg_name} latest version: {response.text}')


if __name__ == '__main__':
    config = {'MONGO_DB_NAME': 'pkg_info', 'MONGO_URL': 'localhost:27017'}
    fetch_package_version(config)
