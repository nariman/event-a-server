"""
Event Bot Server
"""

from eventbot.app import controllers


async def before_start_listener(app, loop):
    """Server listener for controllers registration."""
    app.add_route(controllers.EventsController.as_view(), "/events")
