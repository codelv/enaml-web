"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Jun 14, 2018

@author: jrm
"""
import io
from atom.api import (
    Atom, Dict, Str, Int, Float, Instance, Bool, Property, Enum, Subclass, 
    Tuple, ForwardInstance
)


try:
    import ujson as json
except ImportError:
    import json


def web_application():
    from web.core.app import WebApplication
    return WebApplication


class File(Atom):
    #: Name of file uploaded
    name = Str()
    
    #: Content type of file uploaded
    content_type = Str()
    
    #: Some stream object
    stream = Instance(io.IOBase).tag(store=False)
    
        
class Request(Atom):
    """ A request abstraction object
    
    """
    __slots__ = ('__weakref__',)
    
    #: Request headers
    headers = Instance(dict)
    
    #: Http version
    version = Str()
    
    #: Request method
    method = Str()
    
    #: Request cookies
    cookies = Instance(dict)

    #: URL Scheme
    scheme = Str()
    
    #: Full url
    url = Str()
    
    #: Host
    host = Str()
    
    #: IP Address
    addr = Str()
    
    #: Path
    path = Str()
    
    #: Remote IP addr
    remote_addr = Str()
    
    #: Port
    port = Int()
    
    #: Content type
    content_type = Str() 
    
    #: Content length
    content_length = Int()
    
    #: URL Params
    params = Instance(dict)

    #: Form data
    form = Instance(dict)

    #: File data
    files = Instance(dict)

    #: Some stream object
    stream = Instance(io.IOBase).tag(store=False)
    
    #: Args passed to the handler
    args = Tuple()
    
    #: Kwargs passed to the handler
    kwargs = Dict()
    
    def __repr__(self):
        if self.method is None or not self.path:
            return '<{0}>'.format(self.__class__.__name__)
        return '<{0}: {1} {2}>'.format(self.__class__.__name__,
                                       self.method,
                                       self.path)

    def _load_json(self):
        return ujson.loads(self.stream)

    #: Cached property that will load and cache 
    json = Property(_load_json, cached=True)
    
    
class Response(Atom):
    """ A request abstraction object
    
    """
    __slots__ = ('__weakref__',)
    
    #: Response headers
    headers = Instance(dict)
    
    #: Response cookies
    cookies = Instance(dict)

    #: Response status code
    #: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
    status = Int(200)
    
    #: Some stream object
    stream = Instance(io.IOBase).tag(store=False)
    
    #: The request this response is for
    request = Instance(Request)
    
    #: Content type
    content_type = Str("text/html; charset=utf-8")
    
    #: Redirect to this location
    location = Str()
    
    def _default_stream(self):
        return io.BytesIO()
    
    def __repr__(self):
        if self.method is None or not self.path:
            return '<{0}>'.format(self.__class__.__name__)
        return '<{0}: {1} {2}>'.format(self.__class__.__name__,
                                       self.method,
                                       self.path)

    def json(self, data, dumps=json.dumps):
        """ Set the json response """
        self.content_type = 'application/json'
        self.stream.write(dumps(data))
        
    def write(self, data):
        self.stream.write(data)
    
    def finish(self, data=None):
        pass
    
    
class Handler(Atom):
    """ A generic http handler. Add a method for each http method supported
    to handle it.
    
    """
    #: App this delegates too
    app = ForwardInstance(web_application).tag(store=False)
    
    def _default_app(self):
        return web_application().instance()
    
    def __call__(self, *args, **kwargs):
        """ A handler that creates an unpopulated request and response 
        and delegates handling to the application implementation.
        
        """
        return self.app.dispatch_request(self, *args, **kwargs)
        

class WebsocketHandler(Handler):
    """ A generic websocket handler. 
    
    """
    def on_open(self):
        raise NotImplementedError
    
    def on_message(self, message):
        raise NotImplementedError
    
    def on_close(self):
        raise NotImplementedError
    
        
