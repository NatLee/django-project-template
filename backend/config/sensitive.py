"""
SQL
"""

import os

SQL = {
    "default": {
        "ENGINE": os.environ["DB_ENGINE"],
        "NAME": os.environ["DB_NAME"],  # db name
        "USER": os.environ["DB_USER"],  # db user
        "PASSWORD": os.environ["DB_USER_PASSWORD"],  # db password
        "HOST": os.environ["DB_HOST"],  # db host
        "PORT": os.environ["DB_PORT"],  # db port
    },
    "OPTIONS": {"protocol": "TCP"},
}

"""
REDIS
"""
REDIS_HOST = os.environ["REDIS_HOST"]
