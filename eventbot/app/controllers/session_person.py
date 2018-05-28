"""
Event Bot Server
"""

import asyncpgsa
from asyncpg.connection import Connection
from asyncpg.exceptions import PostgresError
from sanic import response
from sanic.views import HTTPMethodView
from sqlalchemy.sql import select

from eventbot.app import models
from eventbot.app import helpers
from eventbot.lib import exceptions
from eventbot.lib import response_wrapper


class SessionPersonController(HTTPMethodView):

    @helpers.db_connections.provide_connection()
    async def put(self, request, event_id, session_id, person_id, connection):
        """Adds person to event session."""

        # Check, is session and person exists
        for name, model, id in [
            ("Session", models.session, session_id),
            ("Person", models.person, person_id)
        ]:
            try:
                query = (select([model.t])
                    .select_from(model.t)
                    .where(model.t.c.id == id))
                query, params = asyncpgsa.compile_query(query)

                try:
                    row = await connection.fetchrow(query, *params)
                except PostgresError:
                    raise exceptions.NotFetchedError

                if not row:
                    raise exceptions.NotFoundError
            except exceptions.NotFoundError:
                return response.json(
                    response_wrapper.error(f"{name} not found"),
                    status=404)

        # If all is ok, add person to session
        query = (models.session_person.t
            .insert()
            .values(session_id=session_id,
                    person_id=person_id))

        # Compile query and execute
        query, params = asyncpgsa.compile_query(query)
        try:
            rows = await connection.execute(query, *params)
        except PostgresError:
            raise exceptions.NotCreatedError

        # Return the HTTP 204
        return response.text("", status=204)

    @helpers.db_connections.provide_connection()
    async def delete(self, request, event_id, session_id, person_id,
                     connection):
        """Removes person from event session."""

        query = (models.session_person.t
            .delete()
            .where(models.session_person.t.c.session_id == session_id)
            .where(models.session_person.t.c.person_id == person_id))

        # Compile query and execute
        query, params = asyncpgsa.compile_query(query)
        try:
            rows = await connection.execute(query, *params)
        except PostgresError:
            raise exceptions.NotUpdatedError

        # Return the HTTP 204
        return response.text("", status=204)
