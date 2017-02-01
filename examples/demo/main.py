import enaml
from web.twisted.tx_application import WebApplication


def main():
    with enaml.imports():
        from server import DemoServer

    app = WebApplication()

    server = DemoServer()
    server.configure()

    # Start the application event loop
    app.start()


if __name__ == "__main__":
    main()