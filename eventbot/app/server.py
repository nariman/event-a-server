"""
Event Bot Server
"""

from . import listeners
from . import middleware
from . import state
from eventbot import config


# Listeners and middleware lists

before_start_listeners = [
    listeners.controllers_registration.before_start_listener,
    listeners.db_connection.before_start_listener
]
"""List of listeners, that will be iterated, and each listener will
be invoked before server start."""

after_start_listeners = []
"""List of listeners, that will be iterated, and each listener will
be invoked after server start."""

before_stop_listeners = []
"""List of listeners, that will be iterated, and each listener will
be invoked before server stop."""

after_stop_listeners = [
    listeners.db_connection.after_stop_listener
]
"""List of listeners, that will be iterated, and each listener will
be invoked after server stop."""

request_middleware = [
]
"""Functions which will be executed before each request to the
server."""

response_middleware = []
"""Functions which will be executed after each request to the
server."""


# Helpers for registering listeners and middleware before server starts

def add_listeners():
    def add(listeners: list, type: str):
        for listener in listeners:
            state.app.listener(type)(listener)

    add(before_start_listeners, "before_server_start")
    add(after_start_listeners, "after_server_start")
    add(before_stop_listeners, "before_server_stop")
    add(after_stop_listeners, "after_server_stop")

    return True

def add_middleware():
    def add(middleware: list, type: str):
        for mw in middleware:
            state.app.middleware(type)(mw)

    add(request_middleware, "request")
    add(response_middleware, "response")

    return True


# Runs the server with configured settings

run = lambda: (add_listeners() and
               add_middleware() and
               state.app.go_fast(host=config.app.HOST,
                                 port=config.app.PORT,
                                 debug=config.app.DEBUG,
                                 workers=config.app.WORKERS))
