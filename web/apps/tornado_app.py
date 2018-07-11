"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Apr 12, 2017

@author: jrm
"""
import tornado.ioloop
import tornado.web
from functools import wraps
from atom.api import Instance, List
from web.core.app import WebApplication


class DelegateHandler(tornado.web.RequestHandler):
    delegate = None
    
    def __init__(self, application, request, delegate):
        super(DelegateHandler, self).__init__(application, request)
        self.delegate = delegate
    
    def __getattr__(self, name):
        print(f"GETATTR {name}")
        f = getattr(self, self.delegate, None)
        if f is None:
            raise tornado.web.HTTPError(405)
        
        @wraps(f)
        def wrapped(self, *args, **kwargs):
            print("DISPATCH")
            return f(self.request, self, *args, **kwargs)
        return wrapped


class TornadoApplication(WebApplication):
    #: Tornado app to run
    app = Instance(tornado.web.Application)
    
    #: IOLoop to run in
    ioloop = Instance(tornado.ioloop.IOLoop)
    
    #: Handlers to add
    handlers = List(tuple)
    
    def _default_app(self):
        return tornado.web.Application(self.handlers)
    
    def _default_ioloop(self):
        return tornado.ioloop.IOLoop.current()
    
    def start(self, **kwargs):
        """ Start the application's main event loop.

        """
        self.app.listen(kwargs.pop('port', self.port))
        self.ioloop.start()

    def stop(self):
        """ Stop the application's main event loop.

        """
        self.ioloop.stop()

    def deferred_call(self, callback, *args, **kwargs):
        """ Invoke a callable on the next cycle of the main event loop
        thread.

        Parameters
        ----------
        callback : callable
            The callable object to execute at some point in the future.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        self.ioloop.add_callback(callback, *args, **kwargs)
    
    def timed_call(self, ms, callback, *args, **kwargs):
        """ Invoke a callable on the main event loop thread at a
        specified time in the future.

        Parameters
        ----------
        ms : int
            The time to delay, in milliseconds, before executing the
            callable.

        callback : callable
            The callable object to execute at some point in the future.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        self.ioloop.call_later(ms/1000.0, callback, *args, **kwargs)
    
    def write_to_websocket(self, websocket, message):
        """ Send message data to the websocket. Subclasses must implement this
        for data binding.

        Parameters
        -----------
        websocket :
            A websocket object for the given toolkit
        message : str or bytes
            Data to send to the websocket

        """
        websocket.write_message(message)
    
    # -------------------------------------------------------------------------
    # HTTP API
    # -------------------------------------------------------------------------
    def dispatch_request(self, handler, request, *args, **kwargs):
        """ Dispatch the request and response. Since this hooks in at the
        application level no conversion is needed on the request. 
        
        """
        method = request.method.lower()
        f = getattr(handler, method, None)
        response = tornado.web.RequestHandler(self.app, request)
        
        if f is None:
            raise tornado.web.HTTPError(405)
        
        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(request, response, *args, **kwargs)
        
        setattr(response, method, wrapped)
        transforms = [t(self.request) for t in self.app.transforms]
        self.deferred_call(response._execute, transforms)

    def add_route(self, route, handler, **kwargs):
        """ Create a route for the given handler
        
        Parameters
        ----------
        route: String
            The route used
        handler: Object
            The application specific handler for this route
        kwargs: Dict
            Any extra kwargs for this route
        
        """
        self.handlers.append((route, handler, kwargs))
    
    def add_static_route(self, route, path, **kwargs):
        """ Create a route for serving static files at the given path.
        
        Parameters
        ----------
        route: String
            The route used
        path: String
            The file path
        kwargs: Dict
            Any extra kwargs for this route
        
        """
        self.add_route(route.rstrip("/")+"/(.*)", 
                       tornado.web.StaticFileHandler, path=path)
        
    def add_error_handler(self, error, handler, **kwargs):
        """ Create a route for serving static files at the given path.
        
        Parameters
        ----------
        error: Exception
            The exception to handle
        handler: web.core.http.Handler
            The handler for this exception
        kwargs: Dict
            Any extra kwarg
        
        """
        raise NotImplementedError
    
    def url_for(self, route, **kwargs):
        """ Return the url for the given route
        
        Parameters
        ----------
        route: String
            The route used
            
        Returns
        -------
        url: String
            The url of the route
        """
        self.app.reverse_url(route, **kwargs)
