import os
import sys
import enaml
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.ioloop import IOLoop
from web.core.app import WebApplication

# Add this folder to syspath if running from a different folder
sys.path.append(os.path.dirname(__file__))

with enaml.imports():
    from index import Index


class MainHandler(RequestHandler):
    view = Index()
    
    def get(self):
        self.write(self.view.render(request=self))


def main():
    enaml_app = WebApplication()
    app = Application([
        (r"/", MainHandler),
        (r"/static/(.*)", StaticFileHandler, {
            "path": os.path.join(os.path.dirname(__file__), "static")
        }),
    ], debug=True)
    app.listen(8888)
    print("Listening on 8888")
    IOLoop.current().start()


if __name__ == "__main__":
    main()
