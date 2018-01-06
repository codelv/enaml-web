"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Aug 2, 2017

@author: jrm
"""
from atom.api import Enum, Unicode, Typed, ForwardTyped, observe
from enaml.core.declarative import d_
from .raw import Raw, ProxyRawNode


class ProxyCode(ProxyRawNode):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: Code)

    def set_language(self, language):
        raise NotImplementedError

    def set_output_format(self, output_format):
        raise NotImplementedError

    def set_highlight_style(self, style):
        raise NotImplementedError


class Code(Raw):
    """ A block for rendering highlighted code.
    Note: You must include the proper style/stylesheets for highlighting.
          for example: https://github.com/richleland/pygments-css
    """
    #: Reference to the proxy
    proxy = Typed(ProxyCode)

    #: Language to parse if none is given it will guess which to use
    language = d_(Unicode())

    #: Output format
    output_format = d_(Enum('html', 'latex', 'rtf'))

    #: Highlighter style to use
    highlight_style = d_(Unicode())

    @observe('language', 'output_format', 'highlight_style')
    def _update_proxy(self, change):
        """ The superclass implementation is sufficient. """
        super(Code, self)._update_proxy(change)
