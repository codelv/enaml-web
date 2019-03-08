"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Aug 2, 2017

@author: jrm
"""
import pygments
from pygments import lexers, formatters
from .lxml_raw import RawComponent
from web.components.code import ProxyCode


class CodeComponent(RawComponent, ProxyCode):

    def _refresh_source(self):
        d = self.declaration
        code = d.source
        if d.language:
            Lexer = lexers.find_lexer_class_by_name(d.language)
            lexer = Lexer()
        else:
            lexer = lexers.guess_lexer(code)
        formatter = formatters.get_formatter_by_name('html')
        source = pygments.highlight(code, lexer=lexer, formatter=formatter)
        super(CodeComponent, self).set_source(source)

    def set_source(self, source):
        self._refresh_source()

    def set_language(self, language):
        self._refresh_source()

    def set_highlight_style(self, style):
        self._refresh_source()
