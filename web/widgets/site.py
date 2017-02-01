'''
Created on Jan 31, 2017

@author: jrm
'''
from atom.api import ForwardTyped, Unicode
from enaml.core.declarative import d_
from enaml.widgets.toolkit_object import ToolkitObject, ProxyToolkitObject

class ProxySite(ProxyToolkitObject):
    """ The abstract definition of a proxy Widget object.

    """
    #: A reference to the Widget declaration.
    declaration = ForwardTyped(lambda: Site)
    
    def set_hostname(self, hostname):
        raise NotImplementedError
    
class Site(ToolkitObject):
    #: Site hostname
    hostname = d_(Unicode('localhost'))
    
