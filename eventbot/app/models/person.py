"""
Event Bot Server
"""

import datetime

import pendulum
import sqlalchemy as sa

from . import metadata
from eventbot.lib.sqlalchemy.base import Table
from eventbot.lib.sqlalchemy.types import DateTime


t = table = Table(
    "persons",
    metadata,

    sa.Column("id", sa.BigInteger, primary_key=True),
    sa.Column("name", sa.String(1024), nullable=False)
)
