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
    "user_saved_events",
    metadata,

    sa.Column("user_id", GUID, nullable=False),
    sa.Column("event_id", GUID, nullable=False),

    sa.Column("saved_at", DateTime, default=pendulum.now, nullable=False)
)
