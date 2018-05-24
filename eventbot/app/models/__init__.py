"""
Event Bot Server
"""

import sqlalchemy as sa

from eventbot.config import sqlalchemy as config


metadata = sa.MetaData()
"""SQLAlchemy Metadata instance."""


from . import event
from . import schedule_item
from . import schedule_item_tag
from . import tag
