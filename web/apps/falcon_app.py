"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Jun 15, 2018

@author: jrm
"""
import os
import falcon
from falcon.routing.util import set_default_responders
from meinheld import server
from atom.api import Instance
from web.core.app import WebApplication


class FalconApplication(WebApplication):
    #: A preconfigured falcon API
    app = Instance(falcon.API, ())
    
    def start(self, **kwargs):
        """ Start the application's main event loop.

        """
        address = (kwargs.pop('host', self.interface),
                       kwargs.pop('port', self.port))
        print("Falcon running on {}".format(address))
        server.listen(address)
        server.run(self.app)

    def stop(self):
        """ Stop the application's main event loop.

        """
        server.shutdown()
        
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
        server.schedule_call(0, callback, *args, **kwargs)
    
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
        #: TODO: This does not work
        server.schedule_call(int(ms/1000.0), callback, *args, **kwargs)

    # -------------------------------------------------------------------------
    # HTTP API
    # -------------------------------------------------------------------------
    def dispatch_request(self, handler, request, response, *args, **kwargs):
        """ Dispatch the request and response. Since this hooks in at the
        application level no conversion is needed on the request. 
        
        """
        f = getattr(handler, request.method.lower())
        response.content_type = 'text/html'
        return f(request, response, *args, **kwargs)
    
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
        
        if not route.startswith('/'):
            raise ValueError("route must start with '/'")

        if '//' in route:
            raise ValueError("route may not contain '//'")
        
        methods = kwargs.pop('methods', ('GET',))
        method_map = {m.upper(): handler for m in methods}
        set_default_responders(method_map)
        self.app._router.add_route(route, method_map, handler, **kwargs)
    
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
        self.app.add_static_route(route, os.path.abspath(path), **kwargs)
        
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
        self.app.add_error_handler(error, handler, **kwargs)
