# -*- encoding: utf-8 -*-
import threading
import asyncio
import socket
import errno
from os import path as P

import tornado.ioloop
import tornado.web

from experiment_visualization.handlers import IndexHandler, EventsHandler, AssetsHandler

from hypernets.utils import logging as hyn_logging
logger = hyn_logging.getLogger(__name__)


class WebApp(tornado.web.Application):

    def __init__(self, event_file, server_port=8888, port_retries=50):
        """
        Utility to make CompeteExperiment instance with HyperGBM.

        Parameters
        ----------
            event_file: str, required
                where to store experiment events
            server_port: int, optional, default is 8888
                http server port
            port_retries: int, optional, default is 50
                how many times to attempt another port if {server_port} is in using.

        Returns
        -------
        Runnable experiment object
        """
        self.event_file = event_file
        self.server_port = server_port
        self.port_retries = port_retries
        static_path = P.join(P.dirname(P.abspath(__file__)), 'assets')
        handlers = [
            (r'/api/events', EventsHandler),
            (r'/(.*?)$', AssetsHandler, {"path": static_path}),
        ]
        super(WebApp, self).__init__(handlers)

        self.http_server_ = None
        self.ioloop_ = None
        self.server_port_ = None

    def _try_binding_port(self):
        for i in range(self.port_retries+1):
            port = self.server_port + i
            try:
                http_server = self.listen(port)
                self.server_port_ = port
                return http_server
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    logger.info('the port %i is already in use, trying another port.' % port)
                    continue
                else:
                    raise e
            except Exception as e:
                raise e
        raise ValueError(f"the maximum number {self.port_retries} of attempts has been reached")

    def start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if self.port_retries > 0:
            self.http_server_ = self._try_binding_port()
        else:
            self.http_server_ = self.listen(self.server_port)
            self.server_port_ = self.server_port

        logger.info(f"experiment visualization http server is running at: http://0.0.0.0:{self.server_port_}")
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
