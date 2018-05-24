"""
Event Bot Server
"""

from collections import OrderedDict


def ok(data):
    """Builds success response structure with a provided data."""
    return OrderedDict([
        ("status", "ok"),
        ("data", data)
    ])


def error(message=None):
    """Builds error response structure with a provided data."""
    return OrderedDict([
        ("status", "error"),
        ("error", OrderedDict(
            message=message
        ))
    ])
