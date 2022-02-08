from hyperboard.app import WebApp

if __name__ == '__main__':
    logfile = "hyperboard/tests/events_example.json"
    webapp_ = WebApp(logfile)
    webapp_.start()
