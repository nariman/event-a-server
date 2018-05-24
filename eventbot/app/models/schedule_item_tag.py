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
    "schedule_item_tags",
    metadata,

    sa.Column("schedule_item_id", sa.BigInteger, nullable=False),
    sa.Column("tag_id", sa.BigInteger, nullable=False),
)
