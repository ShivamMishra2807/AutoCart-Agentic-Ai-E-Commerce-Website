import sys

from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        # Build the assistant's search index in the background when the real server starts, so the first chat is fast.
        if 'runserver' in sys.argv:
            from .agent_graph import warm_up
            warm_up()
