"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on May 20, 2018

@author: jrm
"""
import sys
import socket
import asyncio
from functools import partial
from web.core.http import Request
from web.core.app import WebApplication

from atom.api import (
    Atom, Dict, Str, Enum, Typed, ForwardInstance, Int, Instance, Bool,
    Property, set_default
)

from httptools.parser.parser import URL
from sanic import Sanic
from sanic.server import CIDict
from sanic.request import (
    RequestParameters, parse_url, urlunparse, parse_qs, parse_multipart_form,
    parse_header, SimpleCookie, error_logger,
    DEFAULT_HTTP_CONTENT_TYPE, json_loads, InvalidUsage
)
from sanic.exceptions import NotFound
from sanic.response import StreamingHTTPResponse, HTTPResponse


class SanicRequest(Request):
    """Properties of an HTTP request such as URL, headers, etc."""
    #: Sanic app
    app = Instance(Sanic)
    
    #: Parsed url
    parsed_url = Typed(URL)

    query_string = Str()

    uri_template = Str()

    #: Match info
    match_info = Dict()
    
    #: Transport used
    transport = Instance(object)

    #: Request args
    #args = Typed(RequestParameters, ())

    #: Raw args as dict
    raw_args = Dict()

    stream = Bool()
    
    #: Alias to attr
    ip = Str()

    #: Auth token header
    token = Str()

    #: Body chunks
    body = Instance((list, bytes), factory=list)

    def __init__(self, url_bytes, headers, version, method, transport,
                 **kwargs):
        super(Request, self).__init__(parsed_url=parse_url(url_bytes),
                                      headers=headers,
                                      version=version,
                                      method=method,
                                      transport=transport,
                                      **kwargs)

    def __bool__(self):
        return self.transport is not None
    
    def _default_app(self):
        return SanicApplication.instance()

    def _default_token(self):
        """Attempt to return the auth header token.

        :return: token related to request
        """
        prefixes = ('Bearer', 'Token')
        auth_header = self.headers.get('authorization')

        if auth_header is not None:
            for prefix in prefixes:
                if prefix in auth_header:
                    return auth_header.partition(prefix)[-1].strip()

    def _parse_form(self):
        content_type, parameters = parse_header(self.content_type)
        try:
            if content_type == 'application/x-www-form-urlencoded':
                form = RequestParameters(
                    parse_qs(self.body.decode('utf-8')))
                files = RequestParameters()
            elif content_type == 'multipart/form-data':
                # TODO: Stream this instead of reading to/from memory
                boundary = parameters['boundary'].encode('utf-8')
                form, files = parse_multipart_form(self.body, boundary)
            else:
                form, files = RequestParameters(), RequestParameters()
        except Exception:
            error_logger.exception("Failed when parsing form")
        return form, files

    def _default_form(self):
        form, self.files = self._parse_form()
        return form

    def _default_files(self):
        self.form, files = self._parse_form()
        return files

    def _default_params(self):
        q = self.query_string
        return RequestParameters(parse_qs(q)) if q else RequestParameters()

    def _default_raw_args(self):
        return {k: v[0] for k, v in self.params.items()}

    def _default_cookies(self):
        cookie = self.headers.get('cookie')
        if cookie is None:
            return {}
        cookies = SimpleCookie()
        cookies.load(cookie)
        return {name: cookie.value for name, cookie in cookies.items()}

    def _get_address(self):
        sock = self.transport.get_extra_info('socket')
        if not sock:
            return "", 0
        if sock.family == socket.AF_INET:
            ip, port = (self.transport.get_extra_info('peername') or
                        ("", 0))
        elif sock.family == socket.AF_INET6:
            ip, port, *_ = (self.transport.get_extra_info('peername') or
                            ("", 0, None, None))
        else:
            ip, port = "", 0
        return ip, port

    def _default_ip(self):
        return self.addr

    def _default_addr(self):
        ip, self.port = self._get_address()
        return ip

    def _default_port(self):
        self.addr, port = self._get_address()
        return port

    def _default_remote_addr(self):
        """Attempt to return the original client ip based on X-Forwarded-For.

        :return: original client ip.
        """
        forwarded_for = self.headers.get('x-forwarded-for', '').split(',')
        remote_addrs = [
            addr for addr in [
                addr.strip() for addr in forwarded_for
            ] if addr
        ]
        if len(remote_addrs) > 0:
            return remote_addrs[0]
        return ''

    def _default_scheme(self):
        if self.app.websocket_enabled \
                and self.headers.get('upgrade') == 'websocket':
            scheme = 'ws'
        else:
            scheme = 'http'

        if self.transport.get_extra_info('sslcontext'):
            scheme += 's'

        return scheme

    def _default_host(self):
        # it appears that httptools doesn't return the host
        # so pull it from the headers
        return self.headers.get('host', '')

    def _default_content_type(self):
        return self.headers.get('content-type', DEFAULT_HTTP_CONTENT_TYPE)

    def _default_match_info(self):
        """return matched info after resolving route"""
        return self.app.router.get(self)[2]

    def _default_path(self):
        return self.parsed_url.path.decode('utf-8')

    def _default_query_string(self):
        q = self.parsed_url.query
        return q.decode('utf-8') if q else ''

    def _default_url(self):
        return urlunparse((
            self.scheme,
            self.host,
            self.path,
            None,
            self.query_string,
            None))

    def _load_json(self, loads=json_loads):
        try:
            return loads(self.stream.getvalue())
        except Exception:
            if not self.body:
                return None
            raise InvalidUsage("Failed when parsing body as json")

    #: Load the body as json
    json = Property(_load_json, cached=True)


class SanicApplication(WebApplication):
    """ An application based on MagicStack's uvloop
    
    """
    #: Sanic app
    app = Instance(Sanic)

    #: The event loop
    loop = Instance(asyncio.AbstractEventLoop)
    
    #: Use a custom request object that doesn't need conversion
    request_factory = set_default(SanicRequest)
    
    #: Whether uvloop is used
    using_uvloop = Bool()
        
    websocket_enabled = Bool(True)
    
    def _default_app(self):
        return Sanic(request_class=SanicRequest)
    
    def _default_loop(self):
        try:
            import uvloop
            self.using_uvloop = True
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass
        return asyncio.get_event_loop()

    def start(self, **kwargs):
        """ Start the application's main event loop.

        """
        self.app.run(host=kwargs.pop('host', self.interface),
                     port=kwargs.pop('port', self.port),
                     debug=kwargs.pop('debug', self.debug), 
                     **kwargs)

    def stop(self):
        """ Stop the application's main event loop.

        """
        print("Stopping loop")
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
        # Future
        if isinstance(future, asyncio.Future):
            while not future.done():
                self._run_once()
            return future.result()
        
        # Coroutine / CoroWrapper
        for res in future:
            self._run_once()
        return res.result()
    
    def _run_once(self):
        if self.using_uvloop:
            if not hasattr(self.loop, '_run_once'):
                raise RuntimeError("Requires a patch")
        self.loop._run_once()

    def write_to_websocket(self, websocket, message):
        """ Send message data to a twisted websocket.

        Parameters
        -----------
        websocket :
            A websocket object for the given toolkit
        message : dict, str or bytes
            Data to send to the websocket

        """
        return self.wait_for(websocket.send(message))
    
    # -------------------------------------------------------------------------
    # HTTP API
    # -------------------------------------------------------------------------
    def dispatch_request(self, handler, request, *args, **kwargs):
        """ Dispatch the request and response. Since this hooks in at the
        application level no conversion is needed on the request. 
        
        """
        f = getattr(handler, request.method.lower())
        return f(request, HTTPResponse(content_type='text/html'), *args, 
                 **kwargs)
    
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
        self.app.add_route(handler, route, **kwargs)
    
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
        self.app.static(route, path, **kwargs)
        
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
        self.app.exception(error)(handler)
    
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
        self.app.url_for(route, **kwargs)
