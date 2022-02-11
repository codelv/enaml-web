"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Aug 2, 2017

@author: jrm
"""


from atom.api import Str, Typed, ForwardTyped, observe
from enaml.core.declarative import d_
from .raw import Raw, ProxyRawNode, ChangeDict


class ProxyCode(ProxyRawNode):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: Code)

    def set_language(self, language: str):
        raise NotImplementedError

    def set_highlight_style(self, style: str):
        raise NotImplementedError


class Code(Raw):
    """A block for rendering highlighted code.
    Note: You must include the proper style/stylesheets for highlighting.
          for example: https://github.com/richleland/pygments-css
    """

    #: Reference to the proxy
    proxy = Typed(ProxyCode)

    #: Language to parse if none is given it will guess which to use
    language = d_(Str())

    #: Highlighter style to use
    highlight_style = d_(Str()).tag(attr=False)

    @observe("language", "highlight_style")
    def _update_proxy(self, change: ChangeDict):
        """The superclass implementation is sufficient."""
        super()._update_proxy(change)
