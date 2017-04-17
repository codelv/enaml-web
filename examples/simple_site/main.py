'''
Created on Apr 12, 2017

@author: jrm
'''
import cyclone.web
from models import Site

class Application(cyclone.web.Application,object):
    
    def __init__(self):
        super(Application, self).__init__( 
           Site().handlers,
            xheaders=False
        )
        
if __name__ == "__main__":
    from web.impl.cyclone_app import CycloneApplication
    app = CycloneApplication(port=8888,app=Application())
    app.start()
