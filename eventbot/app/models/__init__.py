"""
Event Bot Server
"""

import sqlalchemy as sa


metadata = sa.MetaData()
"""SQLAlchemy Metadata instance."""


from . import event
from . import schedule_item
from . import schedule_item_tag
from . import tag
