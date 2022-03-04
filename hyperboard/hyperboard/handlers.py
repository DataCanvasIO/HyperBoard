# -*- encoding: utf-8 -*-
import json
import sys
from pathlib import Path
from typing import Optional, Awaitable

from os import path as P

import tornado.websocket
from tornado.log import app_log
from tornado.web import Finish, HTTPError, StaticFileHandler


class RestResult(object):

    def __init__(self, code, body):
        self.code = code
        self.body = body

    def to_json(self):
        result = {"code": self.code, "data": self.body}
        return json.dumps(result)


class RestCode(object):
    Success = 0
    Exception = -1


class BaseHandler(tornado.web.RequestHandler):

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def _handle_request_exception(self, e):

        if isinstance(e, Finish):
            # Not an error; just finish the request without logging.
            if not self._finished:
                self.finish(*e.args)
            return
        try:
            self.log_exception(*sys.exc_info())
        except Exception:
            app_log.error("Error in exception logger", exc_info=True)
        if self._finished:
            return
        if isinstance(e, HTTPError):
            self.send_error_content(str(e))
        else:
            self.send_error_content(str(e))

    def send_error_content(self, msg):
        # msg = "\"%s\"" % msg.replace("\"", "\\\"")
        _s = RestResult(RestCode.Exception, str(msg))
        self.finish(_s.to_json())

    def response(self, result: dict):
        rest_result = RestResult(RestCode.Success, result)
        self.set_header("Content-Type", "application/json")
        self.write(rest_result.to_json())

    def get_request_as_dict(self):
        body = self.request.body
        return json.loads(body)


class IndexHandler(BaseHandler):

    def __init__(self, a, b, **c):
        super().__init__(a, b, **c)

    def get(self, *args, **kwargs):
        self.finish("It's worked")


class EventsHandler(BaseHandler):

    def get_event_file(self):
        app = self.application
        log_file_exp = Path(app.event_file).absolute()
        return log_file_exp

    def get(self, *args, **kwargs):
        event_begin = int(self.get_argument('begin', '0', True))
        event_file = self.get_event_file()
        with open(event_file, 'r', newline='\n') as f:
            events_txt = f.readlines()
        events_dict = [json.loads(event_txt) for event_txt in events_txt]
        selected_events = events_dict[event_begin:]
        self.response({"events": selected_events})


class AssetsHandler(StaticFileHandler):

    MissingResource = ['favicon.ico']

    async def get(self, path, **kwargs):

        if path in self.MissingResource:
            raise tornado.web.HTTPError(404, f"File {path} is missing")

        if path in ['', '/']:
            resource_path = "index.html"
        else:
            absolute_path = self.get_absolute_path(self.root, self.parse_url_path(path))
            if not P.exists(absolute_path):
                resource_path = "index.html"  # handle 404
            else:
                resource_path = path
        await super(AssetsHandler, self).get(resource_path)
