"""
Copyright (c) 2025, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.txt, distributed with this software.
"""

from sys import intern
from atom.api import Atom, Str, PostValidate


class InternStr(Str):
    """A Str member that automatically interns all values"""

    def __init__(self, default="", *, factory=None, strict=True):
        super().__init__(default, factory=factory, strict=strict)
        self.set_post_validate_mode(
            PostValidate.MemberMethod_ObjectOldNew, "intern_str"
        )

    def intern_str(self, obj: Atom, old: str, new: str):
        return intern(new)
