"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Jul 8, 2018

@author: jrm
"""
from __future__ import annotations

from atom.api import Int, Typed, ForwardTyped, observe
from enaml.core.declarative import d_
from .raw import Raw, ProxyRawNode, ChangeDict


class ProxyNotebook(ProxyRawNode):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: Notebook)

    def set_version(self, version: int):
        raise NotImplementedError


class Notebook(Raw):
    """A node for rendering jupyter notebooks."""

    #: Reference to the proxy
    proxy = Typed(ProxyNotebook)

    #: Version
    version = d_(Int(4))

    @observe("version")
    def _update_proxy(self, change: ChangeDict):
        """Update the version"""
        super()._update_proxy(change)
