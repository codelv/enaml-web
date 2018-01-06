"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

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
        Lexer = (
            lexers.find_lexer_class_by_name(d.language) if d.language
            else lexers.guess_lexer(code)
        )
        if Lexer is None:
            raise ValueError("Could not determine the proper lexer for {}. "
                             "Please define it explicitly.".format(d.language))
        formatter = formatters.get_formatter_by_name(d.output_format)
        if not formatter:
            raise ValueError("Could not determine the formatter for {}. "
                             "Please define it explicitly.".format(
                             d.output_format))
        source = pygments.highlight(code,
                                    lexer=Lexer(),
                                    formatter=formatter)
        super(CodeComponent, self).set_source(source)

    def set_source(self, source):
        self._refresh_source()

    def set_language(self, language):
        self._refresh_source()

    def set_output_format(self, output_format):
        self._refresh_source()

    def set_highlight_style(self, style):
        self._refresh_source()
