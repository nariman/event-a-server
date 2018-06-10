"""
Event Bot Server
"""

import sqlalchemy as sa


metadata = sa.MetaData()
"""SQLAlchemy Metadata instance."""


from . import event
from . import location
from . import person
from . import platform
from . import session
from . import session_location
from . import session_person
from . import session_tag
from . import tag
from . import user
from . import user_platform
