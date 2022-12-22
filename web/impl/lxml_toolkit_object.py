"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.txt, distributed with this software.

Created on Apr 12, 2017

@author: jrm
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Type, Union, Optional, Generator
from atom.api import Atom, Bool, Member, Typed, Event, ForwardTyped, Dict, atomref
from lxml.html import tostring
from lxml.etree import _Element, Element, SubElement
from web.components.html import ProxyTag, Tag
from web.core.app import WebApplication


@lru_cache(1024)
def get_fields(cls: Type[Atom]) -> tuple[Member, ...]:
    """Determine the list of attributes to convert to html and cache them.

    Any member tagged with "attr=False" will be ignored any enaml attrs will
    also be ignored.

    """
    web_members = []
    for name, member in cls.members().items():
        meta = member.metadata
        if not meta:
            continue

        # Exclude any attr tags
        if not (meta.get("d_member") and meta.get("d_final")):
            continue

        # Skip any items tagged with attr=false
        elif not meta.get("attr", True):
            continue

        elif isinstance(member, Event):
            continue
        web_members.append(member)
    return tuple(web_members)


class WebComponent(ProxyTag):
    """An lxml implementation of an Enaml ProxyToolkitObject."""

    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(_Element)

    # -------------------------------------------------------------------------
    # Initialization API
    # -------------------------------------------------------------------------
    def create_widget(self):
        """Create the toolkit widget for the proxy object.

        This method is called during the top-down pass, just before the
        'init_widget()' method is called. This method should create the
        toolkit widget and assign it to the 'widget' attribute.

        """
        d = self.declaration
        parent = d.parent.proxy
        self.root = parent.root
        self.widget = SubElement(parent.widget, d.tag)

    def init_widget(self):
        """Initialize the state of the toolkit widget.

        This method is called during the top-down pass, just after the
        'create_widget()' method is called. This method should init the
        state of the widget. The child widgets will not yet be created.

        """
        widget = self.widget
        d = self.declaration

        #: Save ref id
        self.root.cache[d.id] = atomref(self)
        attrib = widget.attrib
        attrib["id"] = d.id
        if d.text:
            widget.text = d.text
        if d.tail:
            widget.tail = d.tail
        if d.alt:
            attrib["alt"] = d.alt
        if d.style:
            self.set_style(d.style)
        if d.cls:
            self.set_cls(d.cls)
        if d.attrs:
            attrib.update(d.attrs)
        if d.clickable:
            attrib["clickable"] = "true"
        if d.draggable:
            attrib["draggable"] = "true"
        if d.onclick:
            attrib["onclick"] = d.onclick
        if d.ondragstart:
            attrib["ondragstart"] = d.ondragstart
        if d.ondragover:
            attrib["ondragover"] = d.ondragover
        if d.ondragend:
            attrib["ondragend"] = d.ondragend
        if d.ondragenter:
            attrib["ondragenter"] = d.ondragenter
        if d.ondragleave:
            attrib["ondragleave"] = d.ondragleave
        if d.ondrop:
            attrib["ondrop"] = d.ondrop

        for m in get_fields(d.__class__):
            name = m.name
            value = getattr(d, name)
            if value is True:
                attrib[name] = name
            elif value:
                attrib[name] = f"{value}"

    # -------------------------------------------------------------------------
    # ProxyToolkitObject API
    # -------------------------------------------------------------------------
    def activate_top_down(self):
        """Activate the proxy for the top-down pass."""
        self.create_widget()
        self.init_widget()

    def destroy(self):
        """A reimplemented destructor.

        This destructor will clear the reference to the toolkit widget
        and set its parent to None.

        """
        widget = self.widget
        if widget is not None:
            parent = widget.getparent()
            if parent is not None:
                parent.remove(widget)
            del self.widget

            # Remove from cache
            self.root.cache.pop(self.declaration.id, None)

        super().destroy()

    def child_added(self, child: WebComponent):
        """Handle the child added event from the declaration.

        This handler will insert the child into the tree at the
        appropriate index.

        """
        w = self.widget
        if w is None:
            return

        # Use insert to put in the correct spot
        d = self.declaration
        assert d is not None
        i = d._child_index(child.declaration)
        w.insert(i, child.widget)

    def child_moved(self, child: WebComponent) -> bool:
        """Handle the child moved event from the declaration.

        This handler will pop the child and insert it in the correct position
        if it isn't already there.

        """
        w = self.widget
        if w is None:
            return False
        # Determine the new index
        d = self.declaration
        assert d is not None
        i = d._child_index(child.declaration)
        j = w.index(child.widget)
        if j == i:
            return False  # Already in the correct spot
        # Delete and re-insert at correct position
        del w[j]
        w.insert(i, child.widget)
        return True

    def child_removed(self, child: WebComponent):
        """Handle the child removed event from the declaration.

        This handler will unparent the child toolkit widget. Subclasses
        which need more control should reimplement this method.

        """
        w = self.widget
        if w is not None:
            w.remove(child.widget)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def render(self, method: str = "html", encoding: str = "unicode", **kwargs) -> str:
        """Render the widget tree into a string"""
        return tostring(self.widget, method=method, encoding=encoding, **kwargs)

    def xpath(self, query: str, **kwargs) -> Generator[WebComponent, None, None]:
        """Get the node(s) matching the query"""
        w = self.widget
        if w is None:
            return None
        nodes = w.xpath(query, **kwargs)
        if not nodes:
            return None

        root = self.root
        assert root is not None
        lookup = root.cache.get
        for node in nodes:
            aref = lookup(node.attrib.get("id"))
            obj = aref() if aref else None
            if obj is None:
                continue
            yield obj

    def parent_widget(self) -> Optional[_Element]:
        """Get the parent toolkit widget for this object.

        Returns
        -------
        result : QObject or None
            The toolkit widget declared on the declaration parent, or
            None if there is no such parent.

        """
        parent = self.parent()
        if parent is not None:
            return parent.widget
        return None

    def child_widgets(self) -> Generator[_Element, None, None]:
        """Get the child toolkit widgets for this object.

        Returns
        -------
        result : iterable of QObject
            The child widgets defined for this object.

        """
        for child in self.children():
            w = child.widget
            if w is not None:
                yield w

    # -------------------------------------------------------------------------
    # Change handlers
    # -------------------------------------------------------------------------
    def set_text(self, text: str):
        w = self.widget
        assert w is not None
        w.text = text

    def set_tail(self, text: str):
        w = self.widget
        assert w is not None
        w.tail = text

    def set_tag(self, tag: str):
        w = self.widget
        assert w is not None
        w.tag = tag

    def set_attrs(self, attrs: dict[str, Any]):
        """Set any attributes not explicitly defined"""
        w = self.widget
        assert w is not None
        w.attrib.update(attrs)

    def set_cls(self, cls: Union[tuple[str], list[str], str]):
        if isinstance(cls, (tuple, list)):
            cls = " ".join(cls)
        w = self.widget
        assert w is not None
        w.attrib["class"] = cls

    def set_style(self, style: Union[dict, str]):
        if isinstance(style, dict):
            style = ";".join(f"{k}:{v}" for k, v in style.items())
        w = self.widget
        assert w is not None
        w.attrib["style"] = style

    def set_attribute(self, name: str, value: Any):
        """Default handler for those not explicitly defined"""
        w = self.widget
        assert w is not None
        if value is True:
            w.attrib[name] = name
        elif value is False:
            del w.attrib[name]
        else:
            w.attrib[name] = f"{value}"

    def set_clickable(self, clickable: bool):
        w = self.widget
        assert w is not None
        w.attrib["clickable"] = "true" if clickable else "false"

    def set_draggable(self, draggable: bool):
        """The draggable attr must be explicitly set to true or false"""
        w = self.widget
        assert w is not None
        w.attrib["draggable"] = "true" if draggable else "false"


class RootWebComponent(WebComponent):
    """A root component"""

    #: Components are cached for lookup by id so xpath queries from lxml
    #: can retrieve their declaration component
    cache = Dict()

    #: Flag to indicate whether this node was rendered. This is used by the
    #: declaration to avoid creating unnecessary modified events.
    rendered = Bool()

    def create_widget(self):
        self.root = self  # This is the root
        self.widget = Element(self.declaration.tag)

    def render(self, *args, **kwargs):
        self.rendered = True
        return super().render(*args, **kwargs)
