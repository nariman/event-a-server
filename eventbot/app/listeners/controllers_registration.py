"""
Event Bot Server
"""

from eventbot.app import controllers


CONTROLLERS_MAP = [
    ("/events", controllers.EventsController),
    ("/events/<event_id>/sessions", controllers.SessionsController)
]


async def before_start_listener(app, loop):
    """Server listener for controllers registration."""
    for route, controller in CONTROLLERS_MAP:
        app.add_route(controller.as_view(), route)
