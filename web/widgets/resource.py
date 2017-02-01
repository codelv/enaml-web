'''
Created on Jan 31, 2017

@author: jrm
'''
from atom.api import ForwardTyped, Unicode
from enaml.core.declarative import d_
from enaml.widgets.toolkit_object import ToolkitObject, ProxyToolkitObject

class ProxyResource(ProxyToolkitObject):
    """ The abstract definition of a proxy Widget object.

    """
    #: A reference to the Widget declaration.
    declaration = ForwardTyped(lambda: Resource)
    
    def set_route(self, route):
        raise NotImplementedError
    
class ProxyStaticResource(ProxyResource):
    """ The abstract definition of a proxy Widget object.

    """
    #: A reference to the Widget declaration.
    declaration = ForwardTyped(lambda: StaticResource)
    
    def set_path(self, path):
        raise NotImplementedError

class Resource(ToolkitObject):
    #: Path for the route
    route = d_(Unicode('/'))
    
class StaticResource(Resource):
    #: Static file path
    path = d_(Unicode('.'))