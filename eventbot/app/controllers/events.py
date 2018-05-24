"""
Event Bot Server
"""

from sanic import response
from sanic.views import HTTPMethodView


class EventsController(HTTPMethodView):

  async def get(self, request):
      return response.text('I am async get method')
