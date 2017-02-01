'''
Created on Jan 31, 2017

@author: jrm
'''

from atom.api import Instance, Dict
from enaml.application import Application, ProxyResolver
from enaml.mime_data import MimeData
from twisted.internet.base import ReactorBase


class DictMimeData(MimeData):
    """ A dictionary implementation of an Enaml MimeData object.

    """
    #: Internal storage for the MimeData.
    _data = Dict()

    def __init__(self, data=None):
        """ Initialize a QtMimeData object.

        Parameters
        ----------
        data : QMimeData, optional
            The mime data to wrap. If not provided, one will be created.

        """
        self._data = data or {}


    def formats(self):
        """ Get a list of the supported mime type formats.

        Returns
        -------
        result : list
            A list of mime types supported by the data.

        """
        return self._data.keys()

    def has_format(self, mime_type):
        """ Test whether the data supports the given mime type.

        Parameters
        ----------
        mime_type : unicode
            The mime type of interest.

        Returns
        -------
        result : bool
            True if there is data for the given type, False otherwise.

        """
        return mime_type in self._data

    def remove_format(self, mime_type):
        """ Remove the data entry for the given mime type.

        Parameters
        ----------
        mime_type : unicode
            The mime type of interest.

        """
        del self._data[mime_type]

    def data(self, mime_type):
        """ Get the data for the specified mime type.

        Parameters
        ----------
        mime_type : unicode
            The mime type of interest.

        Returns
        -------
        result : str
            The data for the specified mime type.

        """
        return self._data[mime_type]

    def set_data(self, mime_type, data):
        """ Set the data for the specified mime type.

        Parameters
        ----------
        mime_type : unicode
            The mime type of interest.

        data : str
            The serialized data for the given type.

        """
        self._data[mime_type] = data

class WebApplication(Application):
    """ A Twisted implementation of an Enaml application.

    A WebApplication uses the Twisted reactor to implement an Enaml UI that
    runs in the local process.

    """
    
    _reactor = Instance(ReactorBase)

    def __init__(self):
        """ Initialize a QtApplication.

        """
        super(WebApplication, self).__init__()
        from twisted.internet import reactor
        self._reactor = reactor
        from web.factories import WEB_FACTORIES
        self.resolver = ProxyResolver(factories=WEB_FACTORIES)

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def start(self):
        """ Start the application's main event loop.

        """
        reactor = self._reactor
        if not getattr(reactor, '_in_event_loop', False):
            reactor._in_event_loop = True
            reactor.run()
            reactor._in_event_loop = False

    def stop(self):
        """ Stop the application's main event loop.

        """
        reactor = self._reactor
        reactor.stop()
        reactor._in_event_loop = False

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
        self._reactor.callFromThread(callback, *args, **kwargs)

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
        self._reactor.callLater(ms/1000.0, callback, *args, **kwargs)

    def is_main_thread(self):
        """ Indicates whether the caller is on the main gui thread.

        Returns
        -------
        result : bool
            True if called from the main gui thread. False otherwise.

        """
        raise NotImplementedError

    def create_mime_data(self):
        """ Create a new mime data object to be filled by the user.
 
        Returns
        -------
        result : QtMimeData
            A concrete implementation of the MimeData class.
 
        """
        return DictMimeData()
