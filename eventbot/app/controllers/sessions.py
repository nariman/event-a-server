"""
Event Bot Server
"""

import asyncio

import asyncpgsa
import pendulum
from asyncpg.connection import Connection
from asyncpg.exceptions import PostgresError
from sanic import response
from sanic.views import HTTPMethodView
from sqlalchemy.sql import select

from eventbot.app import models
from eventbot.app import helpers
from eventbot.lib import exceptions
from eventbot.lib import response_wrapper


class SessionsController(HTTPMethodView):
    """Event schedule information controller."""

    @helpers.db_connections.provide_connection()
    async def get(self, request, event_id, connection):
        """Returns a list of event sessions aka schedule.

        This endpoint returns complete list, w/o support of listing.
        """

        # Check, is event exists
        try:
            query_event = (select([models.event.t])
                .select_from(models.event.t)
                .where(models.event.t.c.id == event_id)
                .apply_labels())
            query_event, params = asyncpgsa.compile_query(query_event)

            try:
                row = await connection.fetchrow(query_event, *params)
            except PostgresError:
                raise exceptions.NotFetchedError

            if not row:
                raise exceptions.NotFoundError

            event = models.event.t.parse(row, prefix="events_")
        except exceptions.NotFoundError:
            return response.json(
                response_wrapper.error("Event not found"),
                status=404)

        # If event exists, query all sessions
        query = (select([models.session.t])
            .select_from(models.session.t)
            .where(models.session.t.c.event_id == event["id"])
            .order_by(models.session.t.c.start_time.asc())
            .order_by(models.session.t.c.end_time.asc())
            .order_by(models.session.t.c.created_at.asc())
            .order_by(models.session.t.c.id.desc())
            .apply_labels())

        # Compile query, execute and parse
        query, params = asyncpgsa.compile_query(query)
        try:
            rows = await connection.fetch(query, *params)
        except PostgresError:
            raise exceptions.NotFetchedError

        sessions = [
            models.session.json_format(models.session.t.parse(row, prefix="sessions_"))
            for row in rows
        ]

        # Construct sessions map for fetching persons, locations and tags
        smap = {session["id"]: session for session in sessions}
        sids = list(smap.keys())

        # Query all persons, locations and tags ids for sessions
        # TODO: Optimizations
        for name, field, model in [
            ("persons", "person_id", models.session_person),
            ("locations", "location_id", models.session_location),
            ("tags", "tag_id", models.session_tag)
        ]:
            for session in sessions:
                session[name] = []

            query = (select([model.t])
                .select_from(model.t)
                .where(model.t.c.session_id.in_(sids)))  # Probably, hot spot

            query, params = asyncpgsa.compile_query(query)
            try:
                rows = await connection.fetch(query, *params)
            except PostgresError:
                raise exceptions.NotFetchedError

            rows = [model.t.parse(row) for row in rows]
            for row in rows:
                smap[str(row["session_id"])][name].append(str(row[field]))

        # Return the list
        return response.json(response_wrapper.ok(sessions))

    @helpers.db_connections.provide_connection()
    async def post(self, request, event_id, connection):
        """Creates a new event session."""

        # Session form
        session = request.json

        # Check, is event exists
        try:
            query_event = (select([models.event.t])
                .select_from(models.event.t)
                .where(models.event.t.c.id == event_id)
                .apply_labels())
            query_event, params = asyncpgsa.compile_query(query_event)

            try:
                row = await connection.fetchrow(query_event, *params)
            except PostgresError:
                raise exceptions.NotFetchedError

            if not row:
                raise exceptions.NotFoundError

            event = models.event.t.parse(row, prefix="events_")
        except exceptions.NotFoundError:
            return response.json(
                response_wrapper.error("Event not found"),
                status=404)

        # If event exists, create a transaction
        # We need to 1) save session, 2) fetch session from a database
        async with connection.transaction():
            try:
                query = (models.session.t
                    .insert()
                    .values(event_id=event["id"],
                            title=session["title"],
                            description=session["description"],
                            start_time=pendulum.parse(session["start_time"]),
                            end_time=pendulum.parse(session["end_time"]))
                    .returning(models.session.t.c.id))
                query, params = asyncpgsa.compile_query(query)

                id = await connection.fetchval(query, *params)

                query = (select([models.session.t])
                    .select_from(models.session.t)
                    .where(models.session.t.c.id == id)
                    .apply_labels())
                query, params = asyncpgsa.compile_query(query)

                try:
                    row = await connection.fetchrow(query, *params)
                except PostgresError:
                    raise exceptions.NotFetchedError

                if not row:
                    raise exceptions.NotFoundError

                session = models.session.json_format(
                    models.session.t.parse(row, prefix="sessions_"))
            except (PostgresError, exceptions.DatabaseError):
                raise exceptions.NotCreatedError

        for session in sessions:
            for name in ["persons", "locations", "tags"]:
                session[name] = []

        return response.json(response_wrapper.ok(session), status=201)
