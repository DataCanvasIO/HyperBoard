# -*- encoding: utf-8 -*-
import threading
import asyncio

import tornado.ioloop
import tornado.web

from experiment_visualization.handlers import IndexHandler, EventsHandler, AssetsHandler
from os import path as P


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

        self.http_server_ = None
        self.ioloop_ = None

    def start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.http_server_ = self.listen(self.server_port)
        print(f"server is running at: 0.0.0.0:{self.server_port} ")
        self.ioloop_ = tornado.ioloop.IOLoop.instance()
        self.ioloop_.start()

    def stop(self):
        # exit the thread
        self.http_server_.stop()
        self.ioloop_.add_callback(self.ioloop_.stop)


class WebAppRunner(threading.Thread):

    def __init__(self, webapp):
        super(WebAppRunner, self).__init__()
        self.webapp = webapp

    def run(self) -> None:
        self.webapp.start()

    def stop(self):
        self.webapp.stop()
