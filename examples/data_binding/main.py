'''
Created on Apr 12, 2017

@author: jrm
'''
import enaml
import tornado.web
import tornado.websocket
from tornado.web import StaticFileHandler
from models import Company

#: Create instance, load from disk, db, etc.. 
current_company = Company()

class DemoHandler(tornado.websocket.WebSocketHandler):
    """ Handler that supports both websockets and regular requests. """
    view = None # Holds the View,  
    
    def is_websocket(self):
        return self.request.headers.get("Upgrade","").lower() == "websocket"
    
    def initialize(self):
        """ Load the view on first load could also load based on session, group, etc.. 
        """
        if self.__class__.view:
            self.view.handler = self
            self.view.request = self.request
            return
        
        #: Load the View class from the dotted view name
        with enaml.imports():
            from views.index import View
        
        #: Set initial view properties
        self.__class__.view = View(
            company=current_company,
            request=self.request,
            handler=self,
        )
        
    def get(self, *args, **kwargs):
        #: Render view for get request, view is cached for websocket
        """ Execute the correct handler depending on what is connecting. """
        if self.is_websocket():
            return super(DemoHandler, self).get(*args, **kwargs)
        else:
            #return tornado.web.RequestHandler.get(self, *args, **kwargs)
            self.write(self.view.render())
        
    def open(self, *args, **kwargs):
        if self.is_websocket():
            #: When we get a websocket connection 
            #: set the websocket property of the view so
            #: it can notify the client of changes
            self.view.websockets.append(self)
        
    def on_message(self, message):
        """ When enaml.js sends a message """
        #: Decode message
        change = tornado.escape.json_decode(message)
        #print change
        #: Get the owner ID
        ref = change.get('ref')
        if not ref:
            return
        
        #: Get the server side representation of the node
        #: If found will return the View declaration node
        node = self.view.xpath('//*[@ref="{}"]'.format(ref),first=True)
        if node is None:
            return
        
        #: Handle the event
        if change.get('type') and change.get('name'):
            if change['type']=='event':
                #: Trigger the event
                trigger = getattr(node,change['name'])
                trigger()
            if change['type']=='update':
                #: Trigger the update
                setattr(node,change['name'],change['value'])
        
        #: TODO: Apply change??
        
    def on_close(self):
        if self.is_websocket():
            self.view.websockets.remove(self)


class Application(tornado.web.Application,object):
    def __init__(self):
        super(Application, self).__init__([
                (r'/',DemoHandler) ,
                (r"/static/(.*)",StaticFileHandler,{'path':'static/'}) ,
           ],
        )
        
if __name__ == "__main__":
    from web.impl.tornado_app import TornadoApplication
    app = TornadoApplication(port=8888,app=Application(),interface="0.0.0.0")
    app.start()
