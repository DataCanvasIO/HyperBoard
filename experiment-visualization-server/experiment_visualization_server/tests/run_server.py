from experiment_visualization_server.app import WebApp

if __name__ == '__main__':
    logfile = "experiment_visualization_server/tests/events_example.json"
    webapp_ = WebApp(logfile)
    webapp_.start()
