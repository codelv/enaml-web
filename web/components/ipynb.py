"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Jul 8, 2018

@author: jrm
"""
from atom.api import Enum, Unicode, Int, Typed, ForwardTyped, observe
from enaml.core.declarative import d_
from .raw import Raw, ProxyRawNode


class ProxyNotebook(ProxyRawNode):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: Notebook)

    def set_version(self, version):
        raise NotImplementedError


class Notebook(Raw):
    """ A node for rendering jupyter notebooks.
    
    """
    #: Reference to the proxy
    proxy = Typed(ProxyNotebook)
    
    #: Version
    version = Int(4)
    
    @observe('version')
    def _update_proxy(self, change):
        """ Update the version """
        super(Notebook, self)._update_proxy(change)
