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
from web.components.code import ProxyCode
from .lxml_raw import RawComponent, SourceType


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

    def set_source(self, source: SourceType):
        if isinstance(source, str):
            source = highlight(source, lexer=self.lexer, formatter=self.formatter)
        super().set_source(source)

    def set_language(self, language: str):
        d = self.declaration
        assert d is not None
        self.lexer = self._default_lexer()
        self.set_source(d.source)

    def set_highlight_style(self, style: str):
        d = self.declaration
        assert d is not None
        self.formatter = self._default_formatter()
        self.set_source(d.source)
