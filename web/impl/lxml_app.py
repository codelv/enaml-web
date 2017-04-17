'''
Created on Apr 17, 2017

@author: jrm
'''
from atom.api import Int, Unicode
from enaml.application import Application, ProxyResolver
from web.impl import lxml_components

class LxmlApplication(Application):
    #: Port to listen on 
    port = Int(8888)
    
    #: Interface to listen on
    interface = Unicode("127.0.0.1")
    
    def __init__(self,*args,**kwargs):
        """ Initialize a WebApplication.

        """
        super(LxmlApplication, self).__init__(*args,**kwargs)
        self.resolver = ProxyResolver(factories=lxml_components.FACTORIES)
    