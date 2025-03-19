import os
import pytest
import enaml
from jinja2 import Template

TEMPLATE_DIR = os.path.dirname(__file__)

with enaml.imports():
    from pages import HelloWorld, Simple, ListView


@pytest.mark.benchmark(group="hello")
def test_hello_world_jinja(app, benchmark):
    with open("{}/templates/hello_world.html".format(TEMPLATE_DIR)) as f:
        tmpl = f.read()

    @benchmark
    def render():
        Template(tmpl).render()


@pytest.mark.benchmark(group="hello")
def test_hello_world_jinja_prebuilt(app, benchmark):
    with open("{}/templates/hello_world.html".format(TEMPLATE_DIR)) as f:
        tmpl = f.read()
    template = Template(tmpl)

    @benchmark
    def render():
        template.render()


@pytest.mark.benchmark(group="hello")
def test_hello_world(app, benchmark):
    @benchmark
    def render():
        HelloWorld().render()


@pytest.mark.benchmark(group="hello")
def test_hello_world_prebuilt(app, benchmark):
    view = HelloWorld()

    @benchmark
    def render():
        view.render()


NAVIGATION = [
    {"href": "http://python.org", "caption": "Python"},
    {
        "href": "http://jinja.pocoo.org/docs/2.10/templates/",
        "caption": "Template Designer Documentation",
    },
    {"href": "https://github.com/channelcat/sanic", "caption": "Sanic"},
] * 3


@pytest.mark.benchmark(group="simple")
def test_simple_jinja_prebuilt(app, benchmark):
    with open("{}/templates/simple.html".format(TEMPLATE_DIR)) as f:
        template = Template(f.read())

    @benchmark
    def render():
        template.render(navigation=NAVIGATION, content="This is the content")


@pytest.mark.benchmark(group="simple")
def test_simple_jinja(app, benchmark):
    with open("{}/templates/simple.html".format(TEMPLATE_DIR)) as f:
        tmpl = f.read()

    @benchmark
    def render():
        Template(tmpl).render(navigation=NAVIGATION, content="This is the content")


@pytest.mark.benchmark(group="simple")
def test_simple(app, benchmark):
    @benchmark
    def render():
        Simple().render(navigation=NAVIGATION, content="This is the content")


@pytest.mark.benchmark(group="simple")
def test_simple_prebuilt(app, benchmark):
    view = Simple()

    @benchmark
    def render():
        view.render(navigation=NAVIGATION, content="This is the content")


@pytest.mark.benchmark(group="list-add")
def test_list_init(app, benchmark):
    @benchmark
    def render():
        view = ListView(iterable=range(1000))
        view.render()


@pytest.mark.benchmark(group="list-add")
def test_list_update(app, benchmark):
    @benchmark
    def render():
        view = ListView(iterable=[])
        view.render()
        view.render(iterable=range(1000))
