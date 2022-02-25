from tornado.testing import AsyncHTTPTestCase
import json
from experiment_visualization.app import WebApp, WebAppRunner
import time
from pathlib import Path
test_source_dir = Path(__file__).parent


class TestWebApp(AsyncHTTPTestCase):
    logfile = "experiment_visualization/tests/events_example.json"

    def get_app(self):
        webapp_ = WebApp(self.logfile)
        return webapp_

    def fetch_events(self, begin=0):
        response = self.fetch('/api/events?begin='+str(begin))
        self.assertEqual(response.code, 200)
        response_text = str(response.body, encoding='utf-8')
        response_dict = json.loads(response_text)
        assert response_dict['code'] == 0
        events_resp = response_dict['data']['events']
        return events_resp

    def test_fetch_all_events(self):
        events_resp = self.fetch_events(0)
        with open(self.logfile, 'r', newline='\n') as f:
            events_infile = [json.loads(line) for line in f.readlines()]
        self.assertEqual(events_resp, events_infile)

    def test_limit_events(self):
        events_resp = self.fetch_events(2)
        with open(self.logfile, 'r', newline='\n') as f:
            events_infile = [json.loads(line) for line in f.readlines()]
        self.assertEqual(events_resp, events_infile[2:])

    def test_fetch_index(self):
        response = self.fetch('')
        self.assertEqual(response.code, 200)
        response_text = str(response.body, encoding='utf-8')
        index_file = (test_source_dir.parent/"assets"/"index.html").as_posix()
        with open(index_file, 'rb') as f:
            index_html = str(f.read(), encoding='utf-8')
        self.assertEqual(index_html, response_text)


def create_runner():
    logfile = "experiment_visualization_server/tests/events_example.json"
    webapp_ = WebApp(logfile)
    runner = WebAppRunner(webapp_)
    return runner


def test_runner_exit():
    runner = create_runner()
    runner.start()
    time.sleep(1)  # wait start
    runner.stop()

    time.sleep(1)  # wait sleep
    assert not runner.is_alive()


def test_attempt_ports():
    runner1 = create_runner()
    runner1.start()

    runner2 = create_runner()
    runner2.start()

    time.sleep(2)
    runner1.stop()
    runner2.stop()

    time.sleep(1)
    assert runner2.webapp.server_port_ != runner1.webapp.server_port_
