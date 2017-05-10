'''
Created on Apr 12, 2017

@author: jrm
'''
import enaml
import cyclone.web
import cyclone.websocket
from cyclone.web import StaticFileHandler
from models import Company

#: Create instance, load from disk, db, etc.. 
current_company = Company()

class DemoHandler(cyclone.websocket.WebSocketHandler):
    """ Handler that supports both websockets and regular requests. """
    view = None # Holds the View,  
    
    def is_websocket(self):
        return self.request.headers.get("Upgrade","").lower() == "websocket"
    
    def _execute(self, transforms, *args, **kwargs):
        """ Execute the correct handler depending on what is connecting. """
        if self.is_websocket():
            return super(DemoHandler, self)._execute(transforms, *args, **kwargs)
        else:
            return cyclone.web.RequestHandler._execute(self, transforms, *args, **kwargs)
    
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
        
    def get(self):
        #: Render view for get request, view is cached for websocket 
        self.write(self.view.render())
        
    def connectionMade(self, *args, **kwargs):
        if self.is_websocket():
            #: When we get a websocket connection 
            #: set the websocket property of the view so
            #: it can notify the client of changes
            self.view.websockets.append(self)
        
    def messageReceived(self, message):
        """ When enaml.js sends a message """
        #: Decode message
        change = cyclone.escape.json_decode(message)
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
        
    def connectionLost(self, reason):
        if self.is_websocket():
            self.view.websockets.remove(self)


class Application(cyclone.web.Application,object):
    def __init__(self):
        super(Application, self).__init__([
                (r'/',DemoHandler) ,
                (r"/static/(.*)",StaticFileHandler,{'path':'static/'}) ,
           ],
            xheaders=False
        )
        
if __name__ == "__main__":
    from web.impl.cyclone_app import CycloneApplication
    app = CycloneApplication(port=8888,app=Application(),interface="0.0.0.0")
    app.start()
