"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on May 26, 2018

@author: jrm
"""
import asyncio
from asyncio.coroutines import iscoroutine, CoroWrapper
import aiohttp.web
from functools import partial
from atom.api import Instance
from web.core.app import WebApplication


from aiohttp.web_request import BaseRequest

#: Equals returns true even though the requests are completely different
BaseRequest.__eq__ = lambda self, other: id(self) == id(other)


class AiohttpApplication(WebApplication):
    """ An application based on AioHttp
    
    """
    #: The app
    app = Instance(aiohttp.web.Application)

    #: Event loop
    loop = Instance(asyncio.BaseEventLoop)
    
    def _default_app(self):
        return aiohttp.web.Application()

    def _default_loop(self):
        return asyncio.get_event_loop()

    def start(self, **kwargs):
        """ Start the application's main event loop.

        """
        aiohttp.web.run_app(self.app,
                            host=kwargs.pop('host', self.interface),
                            port=kwargs.pop('port', self.port),
                            **kwargs)

    def stop(self):
        """ Stop the application's main event loop.

        """
        self.loop.stop()

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
        if kwargs:
            callback = partial(callback, **kwargs)
        self.loop.call_soon_threadsafe(callback, *args)

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
        if kwargs:
            callback = partial(callback, **kwargs)
        self.loop.call_later(ms/1000.0, callback, *args)
    
    def wait_for(self, future):
        """ Run the async task until it finishes.
        
        Returns
        -------
        result : Object
            The return result from the future
        
        """
        loop = self.loop
        
        if iscoroutine(future):
            # Coroutine / CoroWrapper
            coro = CoroWrapper(future)
            for res in coro:
                loop._run_once()
            future = res
        
        # Future
        if isinstance(future, asyncio.Future):
            while not future.done():
                loop._run_once()
            return future.result()

    def write_to_websocket(self, websocket, message):
        """ Send message data to a twisted websocket.

        Parameters
        -----------
        websocket :
            A websocket object for the given toolkit
        message : dict, str or bytes
            Data to send to the websocket

        """
        #: TODO
        self.wait_for(websocket.send(message))
    
    def dispatch_request(self, handler, request, *args, **kwargs):
        """ Dispatch the request and response. Since this hooks in at the
        application level no conversion is needed on the request. 
        
        """
        f = getattr(handler, request.method.lower())
        response = aiohttp.web.Response(content_type='text/html')
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
        for m in kwargs.pop('methods', ('get',)):
            self.app.router.add_route(m, route, handler)
    
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
        self.app.router.add_static(route, path, **kwargs)
        
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
        self.app.router.url_for(route, **kwargs)
