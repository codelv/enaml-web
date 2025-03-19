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
from atom.api import Atom, Bool, Member, Typed, Event, Dict
from lxml.etree import _Element, Element, SubElement, tostring
from web.components.html import ProxyTag


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
        self.root.cache[d.id] = self
        self.widget = SubElement(parent.widget, d.tag)

    def init_widget(self):
        """Initialize the state of the toolkit widget.

        This method is called during the top-down pass, just after the
        'create_widget()' method is called. This method should init the
        state of the widget. The child widgets will not yet be created.

        """
        widget = self.widget
        set_attr = widget.set
        d = self.declaration

        set_attr("id", d.id)
        if v := d.text:
            widget.text = v
        if v := d.tail:
            widget.tail = v
        if v := d.alt:
            set_attr("alt", v)
        if v := d.style:
            self.set_style(v)
        if v := d.cls:
            self.set_cls(v)
        if d.clickable:
            set_attr("clickable", "true")
        if d.draggable:
            set_attr("draggable", "true")
        if v := d.onclick:
            set_attr("onclick", v)
        if v := d.ondragstart:
            set_attr("ondragstart", v)
        if v := d.ondragover:
            set_attr("ondragover", v)
        if v := d.ondragend:
            set_attr("ondragend", v)
        if v := d.ondragenter:
            set_attr("ondragenter", v)
        if v := d.ondragleave:
            set_attr("ondragleave", v)
        if v := d.ondrop:
            set_attr("ondrop", v)
        if attrs := d.attrs:
            for k, v in attrs.items():
                set_attr(k, v)

        for m in get_fields(d.__class__):
            name = m.name
            value = getattr(d, name)
            if value is True:
                widget.set(name, name)
            elif value:
                widget.set(name, f"{value}")

    # -------------------------------------------------------------------------
    # ProxyToolkitObject API
    # -------------------------------------------------------------------------
    def activate_top_down(self):
        """Activate the proxy for the top-down pass."""
        try:
            self.create_widget()
            self.init_widget()
        except Exception as e:
            nodes = getattr(e, "_d_nodes", None)
            if not isinstance(nodes, list):
                nodes = e._d_nodes = []
            nodes.append(self.declaration)
            raise e

    def destroy(self):
        """A reimplemented destructor.

        This destructor will clear the reference to the toolkit widget
        and set its parent to None.

        """
        if self.root is not None:
            if (root := self.root) and (cache := root.cache):
                try:
                    del cache[self.declaration.id]
                except KeyError:
                    pass

            del self.root

        if self.widget is not None:
            parent = self.widget.getparent()
            if parent is not None:
                parent.remove(self.widget)
            self.widget.clear()
            del self.widget

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
        assert child.declaration is not None
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
        assert child.declaration is not None
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
    def render(
        self, method: str = "html", encoding: str = "unicode", **kwargs
    ) -> Union[str, bytes]:
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
        if root := self.root:
            lookup = root.cache.get
            for node in nodes:
                if obj := lookup(node.get("id")):
                    yield obj

    def parent_widget(self) -> Optional[_Element]:
        """Get the parent toolkit widget for this object.

        Returns
        -------
        result : QObject or None
            The toolkit widget declared on the declaration parent, or
            None if there is no such parent.

        """
        if parent := self.parent():
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

    def set_attrs(
        self, attrs: Optional[dict[str, str]], oldattrs: Optional[dict[str, str]]
    ):
        """Set any attributes not explicitly defined"""
        w = self.widget
        assert w is not None
        if attrs and oldattrs:
            # Attrs changed
            for k in oldattrs:
                if k not in attrs:
                    w.attrib.pop(k, None)
            for k, v in attrs.items():
                w.set(k, v)
        elif not attrs and oldattrs:
            # All attrs removed
            for k in oldattrs:
                w.attrib.pop(k, None)
        elif attrs and not oldattrs:
            # Only new attrs
            for k, v in attrs.items():
                w.set(k, v)

    def set_cls(self, cls: Union[tuple[str], list[str], str]):
        if isinstance(cls, (tuple, list)):
            cls = " ".join(cls)
        w = self.widget
        assert w is not None
        w.set("class", cls)

    def set_style(self, style: Union[dict, str]):
        if isinstance(style, dict):
            style = ";".join(f"{k}:{v}" for k, v in style.items())
        w = self.widget
        assert w is not None
        w.set("style", style)

    def set_attribute(self, name: str, value: Any):
        """Default handler for those not explicitly defined"""
        w = self.widget
        assert w is not None
        if value is True:
            w.set(name, name)
        elif value is False:
            w.attrib.pop(name, None)
        else:
            w.set(name, f"{value}")

    def set_clickable(self, clickable: bool):
        w = self.widget
        assert w is not None
        w.set("clickable", "true" if clickable else "false")

    def set_draggable(self, draggable: bool):
        """The draggable attr must be explicitly set to true or false"""
        w = self.widget
        assert w is not None
        w.set("draggable", "true" if draggable else "false")


class RootWebComponent(WebComponent):
    """A root component"""

    #: Components are cached for lookup by id so xpath queries from lxml
    #: can retrieve their declaration component
    cache = Dict()

    #: Flag to indicate whether this node was rendered. This is used by the
    #: declaration to avoid creating unnecessary modified events.
    rendered = Bool()

    def create_widget(self):
        d = self.declaration
        self.root = self.cache[d.id] = self
        self.widget = Element(d.tag)

    def render(self, *args, **kwargs):
        self.rendered = True
        return super().render(*args, **kwargs)

    def destroy(self):
        del self.root
        del self.cache
        super().destroy()
