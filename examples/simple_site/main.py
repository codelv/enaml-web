import sys
import enaml
import asyncio
from web.core.app import WebApplication

from web.components.api import Html

try:
    import tornado
except ImportError:
    print("Please install `tornado`")
    sys.exit(1)

with enaml.imports():
    from index import Index


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(Index().render())

def make_app():
    # Must have at least one application
    app = WebApplication()
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


async def main():
    app = make_app()
    app.listen(8888)
    print("Listening on 8888")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
