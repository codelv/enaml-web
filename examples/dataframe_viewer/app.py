import os
import json
import enaml
import tornado.web
import tornado.websocket
import tornado.ioloop
from tornado.log import enable_pretty_logging
from web.core.app import WebApplication

with enaml.imports():
    from viewer import Viewer

log = tornado.web.app_log

# Files in the repo
BASE_URL = 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master'
CSV_FILES = ['{}/{}.csv'.format(BASE_URL, name) for name in (
    'anscombe',
    'attention',
    'brain_networks',
    'car_crashes',
    'diamonds',
    'dots',
    'exercise',
    'flights',
    'fmri',
    'gammas',
    'iris',
    'mpg',
    'planets',
    'tips',
    'titanic'
)]

# Holds the rendered view so a websocket can retrieve it later
CACHE = {}

class ViewerHandler(tornado.web.RequestHandler):

    def get(self):
        viewer = Viewer(
            request=self.request,
            response=self,
            csv_files=CSV_FILES,
        )

        # Store the viewer in the cache
        CACHE[viewer.id] = viewer

        self.write(viewer.render())


class ViewerWebSocket(tornado.websocket.WebSocketHandler):
    viewer = None

    def open(self):
        # Store the viewer in the cache
        ref = self.get_argument("ref")
        if ref not in CACHE:
            log.error(f"Viewer with ref={ref} does not exist!")
            self.close()
            return

        # Get a viewer reference
        self.viewer = CACHE[ref]

        # Setup an observer to watch changes on the enaml view
        self.viewer.observe('modified', self.on_dom_modified)

    def on_message(self, message):
        """ When we get an event from js, lookup the node and invoke the
        action on the enaml node.

        """
        change = json.loads(message)
        log.debug(f'Update from js: {change}')

        # Lookup the node
        ref = change.get('id')
        if not ref:
            return
        nodes = self.viewer.xpath('//*[@id=$ref]', ref=ref)
        if not nodes:
            return  # Unknown node
        node = nodes[0]

        # Trigger the change on the enaml node
        if change.get('type') and change.get('name'):
            if change['type'] == 'event':
                trigger = getattr(node, change['name'])
                trigger()
            elif change['type'] == 'update':
                # Trigger the update
                setattr(node, change['name'], change['value'])
        else:
            log.warning(f"Unhandled event {self} {node}: {change}")

    def on_dom_modified(self, change):
        """ When an event from enaml occurs, send it out the websocket
        so the client's browser can update accordingly.

        """
        log.debug(f'Update from enaml: {change}')
        self.write_message(json.dumps(change['value']))

    def on_close(self):
        log.debug(f'WebSocket {self} closed')
        if self.viewer is not None:
            self.viewer.unobserve('modified', self.on_dom_modified)


def run():
    enable_pretty_logging()
    # Needed to create enaml components
    enaml_app = WebApplication()

    # Start the tornado app
    app = tornado.web.Application([
        (r'/', ViewerHandler),
        (r'/websocket/', ViewerWebSocket),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {
            'path': os.path.dirname(__file__)}),
    ], debug=True)
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    run()
