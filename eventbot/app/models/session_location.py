"""
Event Bot Server
"""

import datetime

import pendulum
import sqlalchemy as sa

from . import metadata
from eventbot.lib.sqlalchemy.base import Table
from eventbot.lib.sqlalchemy.types import DateTime, GUID


t = table = Table(
    "session_locations",
    metadata,

    sa.Column("session_id", GUID, nullable=False),
    sa.Column("location_id", GUID, nullable=False)
)
