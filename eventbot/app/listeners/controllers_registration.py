"""
Event Bot Server
"""

from eventbot.app import controllers


CONTROLLERS_MAP = [
    ("/events", controllers.EventsController),

    ("/events/<event_id>", controllers.EventController),
    ("/events/<event_id>/sessions", controllers.SessionsController),
    ("/events/<event_id>/persons", controllers.PersonsController),
    ("/events/<event_id>/locations", controllers.LocationsController),
    ("/events/<event_id>/tags", controllers.TagsController),

    ("/events/<event_id>/sessions/<session_id>/persons/<person_id>", controllers.SessionPersonController),
    ("/events/<event_id>/sessions/<session_id>/locations/<location_id>", controllers.SessionLocationController),
    ("/events/<event_id>/sessions/<session_id>/tags/<tag_id>", controllers.SessionTagController)
]


async def before_start_listener(app, loop):
    """Server listener for controllers registration."""
    for route, controller in CONTROLLERS_MAP:
        app.add_route(controller.as_view(), route)
