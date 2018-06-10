"""
Event Bot Server
"""

from eventbot.app import controllers


CONTROLLERS_MAP = [
    ("/users", controllers.UsersController),
    ("/users/<user_id>", controllers.UserController),
    ("/users/<user_id>/saved/events", controllers.UserSavedEventsController),
    ("/users/<user_id>/saved/events/<event_id>", controllers.UserSavedEventController),
    ("/users/<user_id>/platforms/<platform_id>", controllers.UserPlatformsController),
    ("/users/<user_platform_id>/by_platform/<platform_id>", controllers.UserByPlatformController),

    ("/platforms", controllers.PlatformsController),

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
