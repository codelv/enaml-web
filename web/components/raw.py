"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Aug 2, 2017

@author: jrm
"""
from atom.api import ForwardTyped, Str, Typed, observe, set_default
from enaml.core.declarative import d_

from .html import DEFAULT_CHANGE_TYPES, ChangeDict, ProxyTag, Tag


class ProxyRawNode(ProxyTag):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: Raw)

    def set_source(self, source: str):
        raise NotImplementedError


class Raw(Tag):
    """A block that renders it's text as HTML.

    Note: This will ERASE any child elements the the source content!

    """

    #: Reference to the proxy
    proxy = Typed(ProxyRawNode)

    #: Default tag is a div
    tag = set_default("div")

    #: Raw source to parse and display
    source = d_(Str()).tag(attr=False)

    @observe("source", change_types=DEFAULT_CHANGE_TYPES)
    def _update_proxy(self, change: ChangeDict):
        """The superclass implementation is sufficient."""
        super()._update_proxy(change)
