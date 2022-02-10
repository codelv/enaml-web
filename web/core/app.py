"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Apr 17, 2017

@author: jrm
"""
from functools import lru_cache
from enaml.application import Application, ProxyResolver
from web.impl import lxml_components


class WebApplication(Application):
    """Base enaml web application that uses the widgets defined in
    `web.components.html`

    """

    def _default_resolver(self):
        return ProxyResolver(factories=lxml_components.FACTORIES)

    @lru_cache(1024)
    def resolve_proxy_class(self, declaration_class):
        """Cache the resolved value"""
        return super().resolve_proxy_class(declaration_class)
