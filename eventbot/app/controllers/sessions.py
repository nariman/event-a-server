"""
Event Bot Server
"""

import asyncpgsa
import pendulum
from asyncpg.connection import Connection
from asyncpg.exceptions import PostgresError
from sanic import response
from sanic.views import HTTPMethodView
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import func

from eventbot.app import models
from eventbot.app import helpers
from eventbot.lib import exceptions
from eventbot.lib import listing
from eventbot.lib import response_wrapper


class SessionsController(HTTPMethodView):

    @helpers.db_connections.provide_connection()
    async def get(self, request, event_id, connection):
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

        query = (select([models.session.t])
            .select_from(models.session.t)
            .where(models.session.t.c.event_id == event["id"])
            .order_by(models.session.t.c.start_time.asc())
            .order_by(models.session.t.c.end_time.asc())
            .order_by(models.session.t.c.created_at.asc())
            .order_by(models.session.t.c.id.desc())
            .apply_labels())

        query, params = asyncpgsa.compile_query(query)

        try:
            rows = await connection.fetch(query, *params)
        except PostgresError:
            raise exceptions.NotFetchedError

        sessions = [
            models.session.t.parse(row, prefix="sessions_")
            for row in rows
        ]

        for session in sessions:
            session["id"] = str(session["id"])
            session["event_id"] = str(session["event_id"])
            for _ in ["start_time", "end_time", "created_at"]:
                session[_] = session[_].isoformat()

        return response.json(response_wrapper.ok(sessions))

    @helpers.db_connections.provide_connection()
    async def post(self, request, event_id, connection):
        session = request.json

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

                session = models.session.t.parse(row, prefix="sessions_")
            except (PostgresError, exceptions.DatabaseError):
                raise exceptions.NotCreatedError

        session["id"] = str(session["id"])
        session["event_id"] = str(session["event_id"])
        for _ in ["start_time", "end_time", "created_at"]:
            session[_] = session[_].isoformat()

        return response.json(response_wrapper.ok(session), status=201)
