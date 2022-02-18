import os

import enaml
import pytest
from jinja2 import Template

TEMPLATE_DIR = os.path.dirname(__file__)

with enaml.imports():
    from pages import HelloWorld, Simple


@pytest.fixture
def app():
    from web.core.app import WebApplication

    app = WebApplication.instance() or WebApplication()
    yield app


def test_hello_world_jinja(app, benchmark):
    with open("{}/templates/hello_world.html".format(TEMPLATE_DIR)) as f:
        tmpl = f.read()

    @benchmark
    def render():
        Template(tmpl).render()


def test_hello_world(app, benchmark):
    @benchmark
    def render():
        HelloWorld().render()


NAVIGATION = [
    {"href": "http://python.org", "caption": "Python"},
    {
        "href": "http://jinja.pocoo.org/docs/2.10/templates/",
        "caption": "Template Designer Documentation",
    },
    {"href": "https://github.com/channelcat/sanic", "caption": "Sanic"},
] * 3


def test_simple_jinja(app, benchmark):
    with open("{}/templates/simple.html".format(TEMPLATE_DIR)) as f:
        template = Template(f.read())

    @benchmark
    def render():
        template.render(navigation=NAVIGATION, content="This is the content")


def test_simple(app, benchmark):
    view = Simple()

    @benchmark
    def render():
        view.render(navigation=NAVIGATION, content="This is the content")
