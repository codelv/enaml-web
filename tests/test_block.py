import pytest
from textwrap import dedent
from conftest import compile_source


def test_block(app):
    # Test that a block's content is replaced
    Page = compile_source(
        dedent(
            """
    from web.components.api import *
    from web.core.api import *

    enamldef Template(Html):
        alias content
        Head:
            Title:
                text = "Test"
        Body:
            Block: content:
                pass

    enamldef Page(Template):
        Block:
            block = parent.content
            H2:
                text = "It worked!"

    """
        ),
        "Page",
    )
    view = Page()
    print(view.render())
    assert len(view.xpath("/html/body/h2")) == 1


def test_block_unused(app):
    # Test that an unused block retains it's default content
    Page = compile_source(
        dedent(
            """
    from web.components.api import *
    from web.core.api import *

    enamldef Template(Html):
        alias content
        Head:
            Title:
                text = "Test"
        Body:
            Block: content:
                H1:
                    text = "Default"

    enamldef Page(Template):
        pass

    """
        ),
        "Page",
    )
    view = Page()
    print(view.render())
    assert len(view.xpath("/html/body/h1")) == 1


def test_block_replace(app):
    # Test that a used a block's content is replaced in 'replace' mode
    Page = compile_source(
        dedent(
            """
    from web.components.api import *
    from web.core.api import *

    enamldef Template(Html):
        alias content
        Head:
            Title:
                text = "Test"
        Body:
            Block: content:
                H1:
                    text = "Default"
                P:
                    text = "Foo"

    enamldef Page(Template):
        Block:
            block = parent.content
            H2:
                text = "It worked!"

    """
        ),
        "Page",
    )
    view = Page()
    print(view.render())
    assert len(view.xpath("/html/body/h1")) == 0
    assert len(view.xpath("/html/body/p")) == 0
    assert len(view.xpath("/html/body/h2")) == 1


def test_block_append(app):
    # Test that a block's content is retained and new content is appended in
    # append mode
    Page = compile_source(
        dedent(
            """
    from web.components.api import *
    from web.core.api import *

    enamldef Template(Html):
        alias content
        Head:
            Title:
                text = "Test"
        Body:
            Block: content:
                H1:
                    text = "Default"

    enamldef Page(Template):
        Block:
            block = parent.content
            mode = 'append'
            H1:
                text = "Appended"

    """
        ),
        "Page",
    )
    view = Page()
    print(view.render())
    nodes = view.xpath("/html/body/h1")
    assert len(nodes) == 2
    assert nodes[0].text == "Default"
    assert nodes[1].text == "Appended"


def test_block_prepend(app):
    # Test that a block's content is retained and new content is inserted
    # before the default content in prepend mode.
    Page = compile_source(
        dedent(
            """
    from web.components.api import *
    from web.core.api import *

    enamldef Template(Html):
        alias content
        Head:
            Title:
                text = "Test"
        Body:
            Block: content:
                H1:
                    text = "Default"

    enamldef Page(Template):
        Block:
            block = parent.content
            mode = 'prepend'
            H1:
                text = "Prepended"

    """
        ),
        "Page",
    )
    view = Page()
    print(view.render())
    nodes = view.xpath("/html/body/h1")
    assert len(nodes) == 2
    assert nodes[0].text == "Prepended"
    assert nodes[1].text == "Default"


def test_block_replace_changed(app):
    # Test that a block's content is updated when the blocks content is updated
    Page = compile_source(
        dedent(
            """
    from web.components.api import *
    from web.core.api import *

    enamldef Template(Html):
        alias content
        Head:
            Title:
                text = "Test"
        Body:
            Block: content:
                H1:
                    text = "Default"

    enamldef Page(Template):
        attr names = ['alice']
        Block:
            block = parent.content
            Looper:
                iterable << names
                H2:
                    text = loop_item

    """
        ),
        "Page",
    )
    view = Page()
    print(view.render())
    assert len(view.xpath("/html/body/h1")) == 0
    assert len(view.xpath("/html/body/h2")) == 1

    # Update
    print(view.render(names=["alice", "bob"]))
    assert len(view.xpath("/html/body/h1")) == 0
    assert len(view.xpath("/html/body/h2")) == 2

    print(view.render(names=["tom"]))
    assert len(view.xpath("/html/body/h1")) == 0
    nodes = view.xpath("/html/body/h2")
    assert len(nodes) == 1
    assert nodes[0].text == "tom"


@pytest.mark.parametrize("mode", ("replace", "prepend", "append"))
def test_block_inserting_into_another_block(app, mode):
    # IDK why this would ever happen
    # Should just use the target block directly
    CustomPage = compile_source(
        dedent(
            """
    from web.components.api import *
    from web.core.api import *

    enamldef Template(Html):
        alias body
        alias content
        Head:
            Title:
                text = "Test"
        Body: body:
            Block: content:
                H1:
                    text = "Default"

    enamldef Page(Template):
        alias custom
        Block: custom:
            block = parent.content
            H2:
                text = "bob"

    enamldef CustomPage(Page):
        attr extra = ['jill']
        Block:
            block = custom
            mode = "{mode}"
            Looper:
                iterable << extra
                H3:
                    text = loop_item

    """.format(
                mode=mode
            )
        ),
        "CustomPage",
    )
    view = CustomPage()
    print(view.render())
    assert len(view.xpath("/html/body/h1")) == 0
    n = 0 if mode == "replace" else 1
    assert len(view.xpath("/html/body/h2")) == n
    node_text = [n.text for n in view.xpath("/html/body/h3")]
    assert node_text == ["jill"]

    print(view.render(extra=["jill", "tom"]))
    node_text = [n.text for n in view.xpath("/html/body/h3")]
    assert node_text == ["jill", "tom"]

    print(view.body.children)
    if mode == "append":
        assert view.body.children[0].tag == "h2"
        assert view.body.children[1].tag == "h3"
    elif mode == "prepend":
        assert view.body.children[0].tag == "h3"
        assert view.body.children[-2].tag == "h2"


def test_block_append_changed(app):
    # Test that a block's content is updated when the blocks content is updated
    Page = compile_source(
        dedent(
            """
    from web.components.api import *
    from web.core.api import *

    enamldef Template(Html):
        alias content
        Head:
            Title:
                text = "Test"
        Body:
            Block: content:
                H1:
                    text = "Default"

    enamldef Page(Template):
        attr names = ['alice']
        Block:
            block = parent.content
            mode = 'append'
            Looper:
                iterable << names
                H1:
                    text = loop_item

    """
        ),
        "Page",
    )
    view = Page()
    print(view.render())
    nodes = view.xpath("/html/body/h1")
    assert len(nodes) == 2
    assert nodes[0].text == "Default"
    assert nodes[1].text == "alice"

    # Update
    print(view.render(names=["alice", "bob"]))
    nodes = view.xpath("/html/body/h1")
    assert len(nodes) == 3
    assert nodes[0].text == "Default"
    assert nodes[1].text == "alice"
    assert nodes[2].text == "bob"

    # Update
    print(view.render(names=["bob"]))
    nodes = view.xpath("/html/body/h1")
    assert len(nodes) == 2
    assert nodes[0].text == "Default"
    assert nodes[1].text == "bob"


def test_block_prepend_changed(app):
    # Test that a block's content is updated when the blocks content is updated
    Page = compile_source(
        dedent(
            """
    from web.components.api import *
    from web.core.api import *

    enamldef Template(Html):
        alias content
        Head:
            Title:
                text = "Test"
        Body:
            Block: content:
                H1:
                    text = "Default"

    enamldef Page(Template):
        attr names = ['alice']
        Block:
            block = parent.content
            mode = 'prepend'
            Looper:
                iterable << names
                H1:
                    text = loop_item

    """
        ),
        "Page",
    )
    view = Page()
    print(view.render())
    nodes = view.xpath("/html/body/h1")
    assert len(nodes) == 2
    assert nodes[0].text == "alice"
    assert nodes[1].text == "Default"

    # Update
    print(view.render(names=["alice", "bob"]))
    nodes = view.xpath("/html/body/h1")
    assert len(nodes) == 3
    assert nodes[0].text == "alice"
    assert nodes[1].text == "bob"
    assert nodes[2].text == "Default"

    # Update
    print(view.render(names=["bob"]))
    nodes = view.xpath("/html/body/h1")
    assert len(nodes) == 2
    assert nodes[0].text == "bob"
    assert nodes[1].text == "Default"


def test_block_mode_changed(app):
    # Test that a block's content is updated when the blocks content is updated
    Page = compile_source(
        dedent(
            """
    from web.components.api import *
    from web.core.api import *

    enamldef Template(Html):
        alias content
        Head:
            Title:
                text = "Test"
        Body:
            Block: content:
                H1:
                    text = "Default"

    enamldef Page(Template): view:
        attr mode = 'append'
        Block:
            block = parent.content
            mode << view.mode
            H1:
                text = 'Mode'

    """
        ),
        "Page",
    )
    view = Page()

    for mode in ("append", "prepend", "append", "prepend"):
        print(view.render(mode=mode))
        nodes = view.xpath("/html/body/h1")
        assert len(nodes) == 2
        i, j = (0, 1) if mode == "append" else (1, 0)
        assert nodes[i].text == "Default"
        assert nodes[j].text == "Mode"


def test_block_ref_changed(app):
    # Test that a block's content is updated when the blocks content is updated
    Page = compile_source(
        dedent(
            """
    from web.components.api import *
    from web.core.api import *

    enamldef Template(Html):
        alias header
        alias footer
        Head:
            Title:
                text = "Test"
        Body:
            Block: header:
                H1:
                    text = "Header"
            Block: footer:
                H1:
                    text = "Footer"


    enamldef Page(Template): view:
        attr block = 'header'
        Block:
            block << parent.header if view.block == 'header' else parent.footer
            mode = 'append'
            H1:
                text = 'Added'

    """
        ),
        "Page",
    )
    view = Page()
    print(view.render(block="header"))
    nodes = view.xpath("/html/body/h1")
    assert len(nodes) == 3
    assert nodes[0].text == "Header"
    assert nodes[1].text == "Added"
    assert nodes[2].text == "Footer"

    print(view.render(block="footer"))
    nodes = view.xpath("/html/body/h1")
    assert len(nodes) == 3
    assert nodes[0].text == "Header"
    assert nodes[1].text == "Footer"
    assert nodes[2].text == "Added"
