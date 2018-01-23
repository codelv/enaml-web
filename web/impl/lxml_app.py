"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Apr 17, 2017

@author: jrm
"""
import sys
import atexit
import threading
import subprocess
from fnmatch import fnmatch
from atom.api import List, Bool, Int, Unicode, Value
from enaml.application import Application, ProxyResolver
from web.impl import lxml_components


class LxmlApplication(Application):
    """ Base enaml web application that uses the
        widgets defined in `web.components.html`

        Also provides support for auto reloading when source files change
        using watchdog.
    """

    #: Debug mode
    debug = Bool()

    #: Port to listen on 
    port = Int(8888)

    #: Reload automatically when source changes
    auto_reload = Bool()

    #: Reload when a source file within these directories changes
    auto_reload_dirs = List(default=['.'])

    #: Reload when a file matching one of these patterns changes
    auto_reload_patterns = List(default=['*.py', '*.enaml'])

    #: Generic reloader object
    auto_reloader = Value()
    
    #: Interface to listen on
    interface = Unicode("127.0.0.1")

    def _default_auto_reload(self):
        """ By default, reload automatically when in debug mode. """
        return self.debug
    
    def __init__(self, *args, **kwargs):
        """ Initialize a WebApplication.

        """
        super(LxmlApplication, self).__init__(*args, **kwargs)
        self.resolver = ProxyResolver(factories=lxml_components.FACTORIES)
        if self.debug and self.auto_reload:
            self.init_reloader()

    def init_reloader(self):
        """ Initialize reloading. Requires `watchdog`. """
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            print("Warning: Watchdog is required for auto reloading!")
            return

        app = self

        class Reloader(FileSystemEventHandler):
            _reload_count = 0

            def on_any_event(self, event):
                for p in app.auto_reload_patterns:
                    if fnmatch(event.src_path, p):
                        print("Detected changes in {}, scheduling reload..."
                              .format(event.src_path))
                        app.deferred_call(self.queue_reload)

            def queue_reload(self):
                #: This is called from the main thread
                self._reload_count += 1
                app.timed_call(500, self.dequeue_reload)

            def dequeue_reload(self):
                #: This is called from the main thread
                self._reload_count -= 1
                if self._reload_count == 0:
                    app.reload()

        #: Create the observer
        observer = Observer()
        handler = Reloader()
        for path in self.auto_reload_dirs:
            observer.schedule(handler, path, recursive=True)
        observer.start()

        #: Save a reference
        self.auto_reloader = observer

    def stop(self):
        """ Stop and wait for the child to exit. """
        if self.auto_reloader:
            #: Wait for subprocess
            self.auto_reloader.wait()

    def reload(self):
        """ Reload the app when a source file changes. 
        Currently restarts the process. 
        
        """
        if not self.debug or not self.auto_reload:
            return  #: Just in case
        #: Stop reloader
        self.auto_reloader.stop()

        def restart():
            #: Spawn a copy and quit
            args = [sys.executable]+sys.argv
            print("Spawning {}...".format(" ".join(args)))
            subprocess.Popen(args).wait()

        #: Restart on exit
        atexit.register(restart)

        #: Stop
        self.stop()

    def is_main_thread(self):
        """ Indicates whether the caller is on the main gui thread.
        
        Returns
        -------
        result : bool
            True if called from the main gui thread. False otherwise.
        
        """
        return threading.current_thread().name == 'MainThread'

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
