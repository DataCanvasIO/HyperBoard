from experiment_visualization.app import WebApp

if __name__ == '__main__':
    webapp = WebApp("experiment_visualization/tests/events_example.json")
    webapp.start()
