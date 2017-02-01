
from atom.api import Unicode
from web.html.web_toolkit_object import WebToolkitObject
from web.widgets.resource import ProxyResource, ProxyStaticResource

from twisted.web.resource import Resource


class TxResource(WebToolkitObject, ProxyResource):
    
    widget = Typed(Resource)
    
