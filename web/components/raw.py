"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Aug 2, 2017

@author: jrm
"""
from atom.api import Unicode, Typed, ForwardTyped, set_default, observe
from enaml.core.declarative import d_
from .html import Tag, ProxyTag


class ProxyRawNode(ProxyTag):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: Raw)

    def set_source(self, source):
        raise NotImplementedError


class Raw(Tag):
    """ A block that renders it's text as HTML.

    Note: This will ERASE any child elements the the source content!

    """
    #: Reference to the proxy
    proxy = Typed(ProxyRawNode)

    #: Default tag is a div
    tag = set_default("div")

    #: Raw source to parse and display
    source = d_(Unicode())

    @observe('source')
    def _update_proxy(self, change):
        """ The superclass implementation is sufficient. """
        super(Raw, self)._update_proxy(change)
