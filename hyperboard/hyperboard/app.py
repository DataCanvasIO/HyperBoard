# -*- encoding: utf-8 -*-
import threading
import asyncio

import tornado.ioloop
import tornado.web

from hyperboard.handlers import IndexHandler, EventsHandler, AssetsHandler
from hypernets.utils import logging
from os import path as P

logger = logging.get_logger(__name__)


class WebApp(tornado.web.Application):

    def __init__(self, event_file, server_port=8888):

        self.event_file = event_file
        self.server_port = server_port
        static_path = P.join(P.dirname(P.abspath(__file__)), 'assets')
        handlers = [
            (r'/api/events', EventsHandler),
            (r'/(.*?)$', AssetsHandler, {"path": static_path}),
        ]
        super(WebApp, self).__init__(handlers)

    def start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.listen(self.server_port)
        print(f"server is running at: 0.0.0.0:{self.server_port} ")
        tornado.ioloop.IOLoop.instance().start()


class WebAppRunner(threading.Thread):

    def __init__(self, webapp):
        super(WebAppRunner, self).__init__()
        self.webapp = webapp

    def run(self) -> None:
        self.webapp.start()

