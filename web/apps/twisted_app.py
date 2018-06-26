"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Apr 12, 2017

@author: jrm
"""
import sys
import json
from atom.api import Instance
from twisted.internet import reactor, endpoints
from twisted.web import server
from twisted.python import log
from web.apps.web_app import WebApplication


class UtfEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return super(UtfEncoder, self).default(obj)


class TwistedApplication(WebApplication):
    #: Twisted site to run
    site = Instance(server.Site)
    
    #: Endpoint to host the site on
    endpoint = Instance(endpoints._TCPServerEndpoint)
    
    #: Log location
    log = Instance(object, factory=lambda: sys.stdout)
    
    def _default_endpoint(self):
        """ By default return a TCP4ServerEndpoint
            on the given port and interface if none is passed
        """
        return endpoints.TCP4ServerEndpoint(reactor, self.port,
                                            interface=self.interface)
        
    def start(self):
        """ Start the application's main event loop.

        """
        if self.log:
            log.startLogging(self.log)
        self.endpoint.listen(self.site)
        reactor.run()
    
    def stop(self):
        """ Stop the application's main event loop.

        """
        reactor.stop()

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
        reactor.callFromThread(callback, *args, **kwargs)
    
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
        reactor.callLater(ms/1000.0, callback, *args, **kwargs)
        
    def run_until_complete(self, future):
        """ Run the async task until it finishes.
        
        Returns
        -------
        result : Object
            The return result from the future
        
        """
        d = future
        while not d.called:
            reactor.runUntilCurrent()
        return d.result
    
    def write_to_websocket(self, websocket, message):
        """ Send message data to a twisted websocket.

        Parameters
        -----------
        websocket :
            A websocket object for the given toolkit
        message : dict, str or bytes
            Data to send to the websocket

        """
        if isinstance(message, dict):
            message = json.dumps(message, cls=UtfEncoder).encode('utf-8')
        websocket.sendMessage(message)
    
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
