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
    "locations",
    metadata,

    sa.Column("id", GUID, primary_key=True, default=uuid.uuid4),
    sa.Column("event_id", GUID, nullable=False),

    sa.Column("name", sa.String(512), nullable=False),
)


def json_format(location):
    """Returns JSON-ready representation of the location object."""
    return {
        # convert uuid to str
        "id": str(location["id"]),
        # convert uuid to str, w/o event object
        "event_id": str(location["id"]),

        # name as is
        "name": location["name"]
    }
