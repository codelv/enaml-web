"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Apr 17, 2017

@author: jrm
"""
import sys
import threading
from logging import Logger, getLogger
from atom.api import List, Bool, Int, Unicode, Value, Instance, ForwardSubclass
from enaml.application import Application, ProxyResolver
from web.impl import lxml_components


def request_factory():
    from web.core.http import Request
    return Request

def response_factory():
    from web.core.http import Response
    return Response


class WebApplication(Application):
    """ Base enaml web application that uses the widgets defined in 
    `web.components.html`

    """
    
    #: Debug mode
    debug = Bool()

    #: Port to listen on 
    port = Int(8888)

    #: Interface to listen on
    interface = Unicode("127.0.0.1")
    
    #: Logger
    logger = Instance(Logger)
    
    #: Database
    database = Value()
    
    #: Application
    app = Value()
    
    #: Class used to generate the request object. 
    #: Use this if you wish to extend the functionality.
    request_factory = ForwardSubclass(request_factory)
    
    #: Class used to generate the response object. 
    #: Use this if you wish to extend the functionality.
    response_factory = ForwardSubclass(response_factory)
    
    def _default_logger(self):
        return getLogger("enaml")
    
    def __init__(self, *args, **kwargs):
        """ Initialize a WebApplication.

        """
        super(WebApplication, self).__init__(*args, **kwargs)
        self.resolver = ProxyResolver(factories=lxml_components.FACTORIES)
        
    def is_main_thread(self):
        """ Indicates whether the caller is on the main gui thread.
        
        Returns
        -------
        result : bool
            True if called from the main gui thread. False otherwise.
        
        """
        return threading.current_thread().name == 'MainThread'
    
    def wait_for(self, future):
        """ Run the async task until it finishes.
        
        Returns
        -------
        result : Object
            The return result from the future
        
        """
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # Websocket API
    # -------------------------------------------------------------------------
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
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # HTTP API
    # -------------------------------------------------------------------------
    def dispatch_request(self, handler, *args, **kwargs):
        """ Takes the request args and kwargs and populates the abstract
        request and response objects. It shall then call handle_request.
        
        Parameters
        ----------
        handler: web.core.http.Handler
            The handler chosen by the web applications's router.
        args: Tuple
            The args passed by this web application.
        kwargs: Dict
            The kwargs passed by this web application.
            
        Returns
        -------
        result: Object
            The result returned by handle request.
        
        """
        raise NotImplementedError
        
    def handle_request(self, handler, request, response):
        """ Invokes the handler method with the request and response objects
        and converts the response to the expected format for the web server.
        
        Parameters
        ----------
        handler: web.core.http.Hanlder
            The handler and call that with the populated request and response.
        request: web.core.http.Request
            The request object
        response: web.core.http.Response
            The response object. This implementation should convert this
            to the proper type needed by this application.
        
        Returns
        -------
        result: Object
            A proper response expected by this web server.
        
        """
        raise NotImplementedError
    
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
        raise NotImplementedError
    
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
        raise NotImplementedError
    
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
        """ Return the reversed url for the given route
        
        Parameters
        ----------
        route: String
            The route used
            
        Returns
        -------
        url: String
            The url of the route
        """
        raise NotImplementedError
