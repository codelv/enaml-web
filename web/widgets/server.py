'''
Created on Jan 31, 2017

@author: jrm
'''
from atom.api import ForwardTyped, Enum, Int
from enaml.core.declarative import d_
from enaml.widgets.toolkit_object import ToolkitObject, ProxyToolkitObject

class ProxyServer(ProxyToolkitObject):
    """ The abstract definition of a proxy Widget object.

    """
    #: A reference to the Widget declaration.
    declaration = ForwardTyped(lambda: Server)
    
    def set_protocol(self, port):
        raise NotImplementedError
    
    def set_port(self, port):
        raise NotImplementedError
    
class Server(ToolkitObject):
    #: Server protocol
    protocol = d_(Enum('tcp','udp'))
    
    #: Server port
    port = d_(Int(80))
    
