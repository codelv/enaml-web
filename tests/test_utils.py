import pytest
from web.core.speedups import gen_id, lookup_child_index
from web.components.html import Tag


def test_intern_str():
    # Python normally does not intern anything that doesn't look like an attribute
    # Since cls names are likely to be reused they are automatically interned to save space
    t1 = Tag(cls="ms-2")
    assert t1.cls is "ms-2"  # noqa: F632


def test_child_index():
    with pytest.raises(ValueError):
        lookup_child_index(None)
    with pytest.raises(TypeError):
        lookup_child_index("a", None)

    class Foo:
        _children = True

    with pytest.raises(TypeError):
        lookup_child_index(Foo(), None)
    with pytest.raises(TypeError):
        lookup_child_index(Foo(), Foo())

    class Bar:
        def __init__(self, children=None):
            self._children = children or []

    with pytest.raises(TypeError):
        lookup_child_index(Bar(), Bar())

    c = Tag()
    p = Tag()
    assert isinstance(gen_id(c), str)

    p._children = [Tag(), c]
    assert lookup_child_index(p, c) == 1
    p._children = [c, Tag()]
    assert lookup_child_index(p, c) == 0

    with pytest.raises(KeyError):
        assert lookup_child_index(p, Tag())
