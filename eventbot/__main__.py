"""
Event Bot Server
"""

import os
import urllib.parse

from eventbot import config
from eventbot.app import server


# Host and port within a local server

host = os.environ.get("HOST")
port = os.environ.get("PORT")

if host is not None:
    config.app.HOST = host

if port is not None:
    config.app.PORT = int(port)


# Database connection parameters

db = os.environ.get("DATABASE_URL")
pool_min_size = os.environ.get("POOL_MIN_SIZE")
pool_max_size = os.environ.get("POOL_MAX_SIZE")

if db is not None:
    db = urllib.parse.urlparse(db)

    config.db.HOST = db.hostname
    config.db.PORT = int(db.port)
    config.db.USER = db.username
    config.db.PASSWORD = db.password
    config.db.DATABASE = db.path[1:]

if pool_min_size is not None:
    config.db.POOL_MIN_SIZE = int(pool_min_size)

if pool_max_size is not None:
    config.db.POOL_MAX_SIZE = int(pool_max_size)


# Secret for the JWT generation

secret = os.environ.get("SECRET")

if secret is not None:
    config.jose.SECRET = secret


# Application starting

server.run()
