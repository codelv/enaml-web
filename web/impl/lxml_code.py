"""
Copyright (c) 2017-2019, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Aug 2, 2017

@author: jrm
"""
from atom.api import Instance
from pygments import lexers, highlight
from pygments.lexer import Lexer
from pygments.formatters import HtmlFormatter
from .lxml_raw import RawComponent
from web.components.code import ProxyCode


class CodeComponent(RawComponent, ProxyCode):
    #: Lexer used
    lexer = Instance(Lexer)

    #: HTML Formatter
    formatter = Instance(HtmlFormatter)

    def _default_formatter(self):
        return HtmlFormatter(style=self.declaration.highlight_style)

    def _default_lexer(self):
        d = self.declaration
        if d.language:
            return lexers.find_lexer_class_by_name(d.language)()
        return lexers.guess_lexer(d.source)

    def set_source(self, source):
        super(CodeComponent, self).set_source(highlight(
            source,  lexer=self.lexer, formatter=self.formatter))

    def set_language(self, language):
        self.lexer = self._default_lexer()
        self.set_source(self.declaration.source)

    def set_highlight_style(self, style):
        self.formatter = self._default_formatter()
        self.set_source(self.declaration.source)
