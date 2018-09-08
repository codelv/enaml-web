import enaml
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.ioloop import IOLoop
from web.core.app import WebApplication

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
        (r"/static/(.*)", StaticFileHandler, {"path": "static"}),
    ])
    app.listen(8888)
    print("Listening on 8888")
    IOLoop.current().start()


if __name__ == "__main__":
    main()
