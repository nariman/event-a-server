"""
Event Bot Server
"""

import asyncpg
import sqlalchemy as sa


class Table(sa.Table):
    """SQLAlchemy table with a parsing support."""

    def parse(self, record: asyncpg.Record, prefix: str="") -> dict:
        """Parse an :class:`asyncpg.Record` object into dict."""
        parsed = {column.key: None for column in self.columns}

        for key in parsed:
            if prefix + key in record:
                parsed[key] = record[prefix + key]

        return parsed
