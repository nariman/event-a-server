"""
Event Bot Server
"""

import uuid

import sqlalchemy as sa

from . import metadata
from eventbot.lib.sqlalchemy.base import Table
from eventbot.lib.sqlalchemy.types import GUID


t = table = Table(
    "platforms",
    metadata,

    sa.Column("id", GUID, primary_key=True, default=uuid.uuid4),
    sa.Column("slug", sa.String(64), unique=True, nullable=False),

    sa.Column("name", sa.String(128), nullable=False)
)


def json_format(platform):
    """Returns JSON-ready representation of the platform object."""
    return {
        # convert uuid to str
        "id": str(platform["id"]),
        # slug as is
        "slug": platform["slug"],

        # name as is
        "name": platform["name"]
    }
