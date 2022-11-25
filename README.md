# Enaml Web #

[![status](https://github.com/codelv/enaml-web/actions/workflows/ci.yml/badge.svg)](https://github.com/codelv/enaml-web/actions)
[![codecov](https://codecov.io/gh/codelv/enaml-web/branch/master/graph/badge.svg)](https://codecov.io/gh/codelv/enaml-web)
[![Downloads](https://pepy.tech/badge/enaml-web/month)](https://pepy.tech/project/enaml-web/)

A web component toolkit for [enaml](https://github.com/nucleic/enaml) that
let's you build websites in python declaratively.

You can use enaml-web to build "interactive" websites using python, enaml, and a few lines of _simple_ javascript (see the simple pandas [dataframe viewer](https://github.com/codelv/enaml-web/tree/master/examples/dataframe_viewer) example). The view state (dom) is stored on the server as an enaml view and interaction works by syncing changes between
between the client(s) and server using websockets (or polling).

To demonstrate, the following interaction is all handled with enaml-web

![interactive-websites-in-python-with-enaml](https://user-images.githubusercontent.com/380158/44675893-b4ceb380-a9ff-11e8-89e9-9ca2bce7d217.gif)


### Examples

See the examples folder

- [www.codelv.com](https://www.codelv.com/) - Built entirely using enaml-web
- [SMD Component search](https://github.com/frmdstryr/smd-search) - View and search a pandas dataframe

Have a site? Feel free to share it!

### Why?

It makes it easy to build websites without a lot of javascript.

### Short intro

To use enaml web, you simply replace html tags with the enaml component
(the capitalized tag name). For example:

```python
from web.components.api import *

enamldef Index(Html):
    Head:
        Title:
            text = "Hello world"
    Body:
        H1:
            text = "Render a list!"
        Ul:
            Looper:
                iterable = range(3)
                Li:
                    style = 'color: blue' if loop.index & 1 else ''
                    text = loop.item

```

Calling `render()` on an instance of this enaml view then generates the html
from the view. This is shown in the simple case of a static site generator:

```python

import enaml
from web.core.app import WebApplication

# Create an enaml Application that supports web components
app = WebApplication()

# Import Index from index.enaml
with enaml.imports():
    from index import Index

# Render the Index.enaml to index.html
view = Index()
with open('index.html', 'w') as f:
    f.write(view.render())

```

You can also use it in a request handler with your favorite web framework. For example with tornado
web you can do something like this:


```python
import enaml
import tornado.web
import tornado.ioloop
from web.core.app import WebApplication

# Import Index from index.enaml
with enaml.imports():
    from index import Index

class IndexHandler(tornado.web.RequestHandler):
    view = Index()
    def get(self, request):
        return self.view.render(request=request)

class Application(tornado.web.Application):
    def __init__(self):
        super(Application, self).__init__([
                (r'/',IndexHandler)
           ],
        )

if __name__ == "__main__":
    web_app = WebApplication()
    app = Application()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

```

### So what's the advantage over plain html?

It's as simple as html but it's python so you can, loop over lists, render conditionally,
format variables, etc...

Also, it's not just formatting a template,  the server maintains the page state so
you can interact with the page after it's rendered.  This is something that no other
python template frameworks can do (to my knowledge).

### How it works

It simply generates a tree of [lxml](http://lxml.de/) elements.

#### Advantages

1. Inherently secure

Since it's using lxml elements instead of text, your template code is inherently secure from
injection as lxml automatically escapes all attributes. A closing tag cannot be accidentally missed.

The atom framework provides additional security by enforcing runtime type
checking and optional validation.

2. Minified by default

Other templates engines often render a lot of useless whitespace. This does not. The response is always minified.

3. No template tags needed

Some template engines require the use of "template tags" wrapped in `{% %}`
or similar to allow the use of python code to transform variables.

Since enaml _is_ python, you can use any python code directly in
your enaml components and templates. You don't need any template tags.

4. Templates can be modified

The tree can be modified after it's rendered to react to events or data changes. These
changes can be propogated out to clients (see the data binding section).

5. Component based

Since enaml views are like python classes, you can "subclass" and extend any
component and extend it's functionality. This enables you to quickly build
reusable components. This is like "web components" but it's rendered server side
so it's not slow. See [materialize-ui](https://github.com/frmdstryr/materialize) for an example.

#### Disadvantages

1. Memory usage

Even though lxml is written in c and enaml uses atom objects, the memory usage may still
be more than plain string templates.

2. HTML only

It only works with html.


### Data binding

Because enaml-web is generating a dom, you can use websockets and some js
to manipulate the dom to do data binding between the client to server.

The dom can be shared per user or per session making it easy to create
collaborative pages or they can be unique to each page.

![Data binding](https://github.com/frmdstryr/enaml-web/blob/master/docs/data-binding.gif?raw=true)

Each node has a unique identifier and can be modified using change events. An
example of this is in the examples folder.

You can also have the client trigger events on the server and have the server
trigger JS events on the client.

To use:
1. Include a client side script in your page to process modified events
2. Observe the `modified` event of an Html node and pass these changes to the
client via websockets.
3. Make a handlers on the server side to update dom accordingly.


See [app.js](examples/dataframe_viewer/app.js#L7) for an example client
side handler and [app.py](examples/dataframe_viewer/app.py#L70) for an example
server side handler.

##### Modified events

The modified events will be a dict. The keys depend on the event type but the
general format is:

```python
{
  'id': 'id-of-node', # ID of node where the event originated
  'type': 'update', # Type of event, eg, update, added, removed, etc..
  'name': 'attr-modified', # Attr name that was modified, eg `cls` or `children`
  'value': object, # Depends on the event type
  # May have other events
}
```

For example, changing the `style` attribute on a node will generate an event like

```python
{
  'id': 'id-of-a-node',
  'type': 'update',
  'name': 'style',
  'value': 'color: blue',
  'oldvalue': 'color: red'
}
```

Inserting a new list item node will generate an event like

```python
{
  'id': 'id-of-my-list',
  'type': 'added',
  'name': 'children',
  'value': '<li>New item</li>',
  'before': 'id-of-node-to-insert-before', 
}

```

The full list of events can be found in the base [Tag](web/components/html.py)
by searching for `_notify_modified` calls. You can also generate your own
custom events as needed.

#### Data models

Forms can automatically be generated and populated using enaml's DynamicTemplate
nodes. An implementation of the `AutoForm` using the [materalize css](https://github.com/frmdstryr/materialize)
framework is available on my personal repo. With this, we can take a model like:

```python

from atom.api import Atom, Unicode, Bool, Enum

class Message(Atom):
    name = Unicode()
    email = Unicode()
    message = Unicode()
    options = Enum("Email","Phone","Text")
    sign_up = Bool(True)


```

Then use the `AutoForm` node and pass in either a new or populated instance of
the model to render the form.

```python

from templates import Base
from web.components.api import *
from web.core.api import Block


enamldef AddMessageView(Base): page:
    attr message
    Block:
        block = page.content
        AutoForm:
            model << message

```

### Database ORM with Atom

For working with a database using atom see [atom-db](https://github.com/codelv/atom-db)


#### Raw, Markdown, and Code nodes

The`Raw` node parses text into dom nodes (using lxml's html parser). Similarly
`Markdown` and `Code` nodes parse markdown and highlight code respectively.

For example, you can show content from a database like tihs:

```python

from web.components.api import *
from web.core.api import *
from myapp.views.base import Page

enamldef BlogPage(Page):
    attr page_model: SomeModel # Page model
    body.cls = 'template-blogpage'
    Block:
        block = parent.content
        Raw:
            # Render source from database
            source << page_model.body

```

This let's you use web wysiwyg editors to insert content into the dom. If the content
is not valid it will not mess up the rest of the page.


### Block nodes

You can define a base template, then overwrite parts using the `Block` node.

In one file put:

```python

from web.components.api import *
from web.core.api import Block

enamldef Base(Html):
    attr user
    attr site
    attr request
    alias content
    Head:
        Title:
            text << site.title
    Body:
        Header:
            text = "Header"
        Block: content:
            pass
        Footer:
            text = "Footer"

```

Then you can import that view and _extend_ the template and override the
block's content.

```python
from templates import Base
from web.components.api import *
from web.core.api import Block

enamldef Page(Base): page:
    Block:
        block = page.content
        P:
            text = "Content inserted between Header and Footer"

```

Blocks let you either replace, append, or prepend to the content.


### Gotchas

##### Text and tail nodes

Lxml uses text and tail properties to set text before and after child nodes, which can be confusing.

For instance in html you can do

```html

<p>This is a sentence <a href="#">click here</a> then keep going</p>

```

To make this with enaml you need to do this:

```python

P:
    text = "This is a sentence"
    A:
        href = "#"
        text = "click here"
        tail = "then keep going"

```

Notice how `tail` is set on the `A` NOT the `P`.
See [lxml etree documentation](http://lxml.de/tutorial.html#elements-contain-text) for more details.


##### Tag attribute

When creating a custom `Tag`, the `tag` attribute must be set to change what
html tag is used for a node. For example:

```python

enamldef Svg(Tag):
    tag = 'svg' # Force tag to be 'svg'

```

This will then render a `<svg>...</svg>` tag.

> Note: In previous versions (0.8.8 and below) the tag name defaulted to the
lowercase class name. This is no longer done to eliminate a function call per
node and to avoid having to explicitly redefine the tag when subclassing.

##### Generic attributes

The [html](https://github.com/codelv/enaml-web/blob/master/web/components/html.py)
definitions only expose the commonly used attributes of each node,
such as `cls`, `style`, and those specific to the tag (such as or `href` for a link).

Custom attributes or attributes which can't be set as a name in python
(such as `data-tooltip`) can defined by assigning `attrs` to a `dict` of
attr value pairs.

```python
enamldef Tooltip(Span):
    attrs = {'data-tooltip': 'Tooltip text'}
```

This will create a node like:

```html
<span data-tooltip="Tooltip text"></span>
```
