import pytest
from web.core.speedups import gen_id, lookup_child_index
from web.components.html import Tag


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
