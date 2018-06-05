"""
Event Bot Server
"""

import datetime
import uuid

import pendulum
import sqlalchemy as sa

from . import metadata
from eventbot.lib.sqlalchemy.base import Table
from eventbot.lib.sqlalchemy.types import DateTime, GUID


t = table = Table(
    "persons",
    metadata,

    sa.Column("id", GUID, primary_key=True, default=uuid.uuid4),
    sa.Column("event_id", GUID, nullable=False),

    sa.Column("name", sa.String(1024), nullable=False)
)


def json_format(person):
    """Returns JSON-ready representation of the person object."""
    return {
        # convert uuid to str
        "id": str(person["id"]),
        # convert uuid to str, w/o event object
        "event_id": str(person["event_id"]),

        # name as is
        "name": person["name"]
    }
