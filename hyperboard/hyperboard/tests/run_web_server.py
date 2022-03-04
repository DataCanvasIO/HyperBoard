from hyperboard.app import WebApp

if __name__ == '__main__':
    webapp = WebApp("hyperboard/tests/events_example.json")
    webapp.start()
