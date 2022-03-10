"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Aug 2, 2017

@author: jrm
"""
from __future__ import annotations

from typing import Union, Optional
from atom.api import ForwardTyped, Instance, Typed, set_default, observe
from lxml.etree import _Element as Element
from enaml.core.declarative import d_
from .html import Tag, ProxyTag, ChangeDict

SourceType = Optional[Union[str, list[Element], Element]]


class ProxyRawNode(ProxyTag):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: Raw)

    def set_source(self, source: SourceType):
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
    source = d_(Instance((str, list, Element))).tag(attr=False)

    @observe("source")
    def _update_proxy(self, change: ChangeDict):
        """The superclass implementation is sufficient."""
        super()._update_proxy(change)
