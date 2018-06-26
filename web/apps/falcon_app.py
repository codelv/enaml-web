"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Jun 15, 2018

@author: jrm
"""
import os
import falcon
from wsgiref import simple_server
from atom.api import Instance
from web.core.app import WebApplication


class FalconApplication(WebApplication):
    #: A preconfigured falcon API
    app = Instance(falcon.API, ())
    
    #: The server
    loop = Instance(simple_server.WSGIServer)
    
    def start(self, **kwargs):
        """ Start the application's main event loop.

        """
        self.loop = simple_server.make_server(
            kwargs.pop('host', self.interface),
            kwargs.pop('port', self.port),
            self.app, **kwargs)
        self.loop.serve_forever()

    def stop(self):
        """ Stop the application's main event loop.

        """
        self.loop.shutdown()

    # -------------------------------------------------------------------------
    # HTTP API
    # -------------------------------------------------------------------------
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
        self.app.add_route(route, handler, **kwargs)
    
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
