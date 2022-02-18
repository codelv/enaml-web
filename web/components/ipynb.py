"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Jul 8, 2018

@author: jrm
"""
from __future__ import annotations

from atom.api import ForwardTyped, Int, Typed, observe
from enaml.core.declarative import d_

from .raw import D_CHANGE_TYPES, ChangeDict, ProxyRawNode, Raw


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

    @observe("version", change_types=D_CHANGE_TYPES)
    def _update_proxy(self, change: ChangeDict):
        """Update the version"""
        super()._update_proxy(change)
