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
    "tags",
    metadata,

    sa.Column("id", GUID, primary_key=True, default=uuid.uuid4),
    sa.Column("event_id", GUID, nullable=False),

    sa.Column("name", sa.String(1024), nullable=False),
    sa.Column("color", sa.String(8)),
)


def json_format(tag):
    """Returns JSON-ready representation of the tag object."""
    return {
        # convert uuid to str
        "id": str(tag["id"]),
        # convert uuid to str, w/o event object
        "event_id": str(tag["event_id"]),

        # name as is
        "name": tag["name"],
        # color as is, can be null
        "color": tag["color"]
    }
