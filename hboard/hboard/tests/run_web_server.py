from hboard.app import WebApp

if __name__ == '__main__':
    webapp = WebApp("hboard/tests/events_example.json")
    webapp.start()
