"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Apr 15, 2017

@author: jrm
"""
from __future__ import annotations

from typing import Any
from atom.api import ForwardInstance, Enum
from enaml.core.declarative import Declarative, d_

ChangeDict = dict[str, Any]


class Block(Declarative):
    """An object which dynamically insert's its children into another block's
    parent object.

    The 'Block' object is used to cleanly and easily insert it's children
    into the children of another object. The 'Object' instance assigned to the
    'block' property of the 'Block' will be parented with the parent of
    the 'Block'. Creating a 'Block' with no parent is a programming
    error.

    """

    #: The Block to which this blocks children should be inserted into
    block = d_(ForwardInstance(lambda: Block))

    #: If replace, replace all parent's children (except the block of course)
    mode = d_(Enum("replace", "append", "prepend"))

    def initialize(self):
        """A reimplemented initializer.

        This method will add the include objects to the parent of the
        include and ensure that they are initialized.

        """
        super().initialize()
        self.refresh_items()

    def refresh_items(self):
        block = self.block
        if block:
            # This block is setting the content of another block
            before = None

            # Remove the existing blocks children
            if self.mode == "replace":
                # Clear the blocks children
                for c in block.children[:]:
                    block.children.remove(c)
                    if not c.is_destroyed:
                        c.destroy()
            # Add this blocks children to the other block
            elif self.mode == "prepend" and block.children:
                before = block.children[0]

            block.insert_children(before, self.children)

        else:
            # This block is inserting it's children into it's parent
            self.parent.insert_children(self, self.children)

    def _observe_mode(self, change: ChangeDict):
        """If the mode changes. Refresh the items."""
        block = self.block
        if block and self.is_initialized and change["type"] == "update":
            if change["oldvalue"] == "replace":
                raise NotImplementedError
            for c in self.children:
                block.children.remove(c)
                c.set_parent(None)
            self.refresh_items()

    def _observe_block(self, change: ChangeDict):
        """A change handler for the 'objects' list of the Include.

        If the object is initialized objects which are removed will be
        unparented and objects which are added will be reparented. Old
        objects will be destroyed if the 'destroy_old' flag is True.

        """
        if self.is_initialized and change["type"] == "update":
            old_block = change["oldvalue"]
            for c in self.children:
                old_block.children.remove(c)
                c.set_parent(None)
            self.refresh_items()

    def _observe__children(self, change: ChangeDict):
        """When the children of the block change. Update the referenced
        block.

        """
        if not self.is_initialized or change["type"] != "update":
            return

        block = self.block
        new_children = change["value"]
        old_children = change["oldvalue"]
        for c in old_children:
            if c not in new_children and not c.is_destroyed:
                c.destroy()
            else:
                c.set_parent(None)

        if block:
            # This block is inserting into another block
            before = None
            if self.mode == "replace":
                block.children = []
            if self.mode == "prepend" and block.children:
                before = block.children[0]
            block.insert_children(before, new_children)
        else:
            # This block is a placeholder
            self.parent.insert_children(self, new_children)
