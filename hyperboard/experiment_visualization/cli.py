import argparse
from os import path as P


def main():
    description = 'hyperboard command is used to visualize the experiment'
    parser = argparse.ArgumentParser(prog="hyperboard", description=description, add_help=True)

    subparsers = parser.add_subparsers(dest="operation")

    server_parser = subparsers.add_parser("server", help="start webserver")
    server_parser.add_argument("--event-file", help="experiment event file", default=None, required=True)
    server_parser.add_argument("--port", help="server port", default=8888, required=False)

    args_namespace = parser.parse_args()

    def _require_file(path):
        if not P.exists(path):
            raise FileNotFoundError(path)

        if not P.isfile(path):
            raise ValueError(f"Path {path} is not a file ")

    operation = args_namespace.operation
    if operation == 'server':
        event_file = P.abspath(args_namespace.event_file)
        _require_file(event_file)
        server_port = int(args_namespace.port)
        # start web server with the event file
        from experiment_visualization import app
        webapp = app.WebApp(event_file, server_port=server_port)
        webapp.start()
    else:
        parser.print_usage()


if __name__ == '__main__':
    # hyperboard server --event-file=/path/to/event --port=9988
    # hyperboard server --event-file=/path/to/event
    main()
