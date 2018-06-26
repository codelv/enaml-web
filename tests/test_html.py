import enaml
import pytest
import inspect
from utils import compile_source
from textwrap import dedent
from web.core.app import WebApplication

@pytest.fixture
def app():
    app = WebApplication.instance() or WebApplication()
    yield app
    

def test_hello_world(app):
    Page = compile_source(dedent("""
    from web.components.api import *
    
    enamldef Page(Html):
        Head:
            Title:
                text = "Hello world!"
        Body:
            H1: 
                text = "Hello world!"
    """), 'Page')
    view = Page()
    assert view.render()
    
    
def test_looper(app):
    Page = compile_source(dedent("""
    from web.components.api import *
    from web.core.api import *
    
    enamldef Page(Html):
        Head:
            Title:
                text = "Hello world"
        Body:
            Ul:
                Looper:
                    iterable = range(10)
                    Li:
                        text = str(loop_item)
    """), 'Page')
    view = Page()
    print(view.render())
    assert len(view.xpath('//*/li')) == 10
    

def test_raw(app):
    # Test that raw content is rendered
    Page = compile_source(dedent("""
    from web.components.api import *
    from web.core.api import *
    
    enamldef Page(Html): view:
        attr source
        Head:
            Title:
                text = "Test"
        Body:
            Raw: 
                source << view.source 
    """), 'Page')
    view = Page()
    print(view.render(source="<p>Rendered content!</p>"))
    # Use xpath the widget directly
    assert len(view.proxy.widget.xpath('/html/body/div/p')) == 1
    
    print(view.render(source="<h1>Rendered content!</h1>"))
    assert len(view.proxy.widget.xpath('/html/body/div/h1')) == 1
    
def test_markdown(app):
    # Test that raw content is rendered
    Page = compile_source(dedent("""
    from web.components.api import *
    from web.core.api import *
    
    enamldef Page(Html): view:
        attr source
        Head:
            Title:
                text = "Test"
        Body:
            Markdown: 
                source << view.source 
    """), 'Page')
    view = Page()
    print(view.render(source="# Hello world\n"))
    # Use xpath the widget directly
    assert len(view.proxy.widget.xpath('/html/body/div/h1')) == 1
    
    print(view.render(source="\n- Rendered content\n"))
    assert len(view.proxy.widget.xpath('/html/body/div/ul')) == 1
    
    
def test_code(app):
    # Test that raw content is rendered
    Page = compile_source(dedent("""
    from web.components.api import *
    from web.core.api import *
    
    enamldef Page(Html): view:
        attr source
        Head:
            Title:
                text = "Test"
        Body:
            Code: 
                language = "python"
                source << view.source 
    """), 'Page')
    view = Page()
    print(view.render(source=inspect.getsource(compile_source)))
    # Use xpath the widget directly
    assert len(view.proxy.widget.xpath('/html/body/div/div/pre')) == 1
