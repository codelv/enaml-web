# Enaml Web #

[![Build Status](https://travis-ci.org/codelv/enaml-web.svg?branch=master)](https://travis-ci.org/codelv/enaml-web)
[![codecov](https://codecov.io/gh/codelv/enaml-web/branch/master/graph/badge.svg)](https://codecov.io/gh/codelv/enaml-web)
[![Downloads](https://pepy.tech/badge/enaml-web/month)](https://pepy.tech/project/enaml-web/month)

A web component toolkit for [enaml](https://github.com/nucleic/enaml) that
let's you build websites in python declaratively.

> Note: A breaking change was introduced in 0.9.0 usage of `ref` should be replaced with `id`

You can use enaml-web to build "interactive" websites using python, enaml, and a few lines of _simple_ javascript (see the simple pandas [dataframe viewer](https://github.com/codelv/enaml-web/tree/master/examples/dataframe_viewer) example). The view state (dom) is stored on the server as an enaml view and interaction works by syncing changes between
between the client(s) and server using websockets (or polling).

To demonstrate, the following interaction is all handled with enaml-web

![interactive-websites-in-python-with-enaml](https://user-images.githubusercontent.com/380158/44675893-b4ceb380-a9ff-11e8-89e9-9ca2bce7d217.gif)


### Examples

See the examples folder

- [www.codelv.com](https://www.codelv.com/) - Built entirely using enaml-web
- [SMD Component search](https://github.com/frmdstryr/smd-search) - View and search a pandas dataframe


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
            text = "Hello world"

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

It generates a dom of [lxml](http://lxml.de/) elements.

##### Inherently secure

Since an lxml dom is generated it means that your code is inherently secure from
injection as it automatically escapes all attributes. Also a closing tag cannot
be accidentally missed.

The atom framework provides additional security by enforcing runtime type
checking and optional validation.


##### Extendable via templates and blocks

Like other template engines, enaml-web provides a "Block" node that allows
you to define a part of a template that can be overridden or extended.

Enaml also provides pattern nodes for handling conditional statements, loops,
dynamic nodes based on lists or models, and nodes generated from more complex
templates (ex automatic form generation).


##### No template tags needed

Many template engines require the use of "template tags" wrapped in `{% %}`
or similar to allow the use of python code to transform variables.

Since enaml _is_ python, you can use any python code directly in
your enaml components and templates. You don't need any template tags.


##### Testing is easier

Since the internal representation is lxml nodes, you can use lxml's xpath
queries on the dom for e2e view testing. No need to use headless browsers and
that complicated stuff (unless you're using a lot of js).


##### Component based

Since enaml views are like python classes, you can "subclass" and extend any
component and extend it's functionality. This enables you to quickly build
reusable components.

I'm working on components for several common css frameworks so they can simply
be installed and used.

1. [materialize-ui](https://github.com/frmdstryr/materialize)
2. semantic-ui (coming soon)
3. bootstrap (coming soon)


### Data binding

Because enaml-web is generating a dom, you can use websockets and some js
to manipulate the dom to do data binding between the client to server.

The dom can be shared per user or per session making it easy to create
collaborative pages or they can be unique to each page.

![Data binding](https://github.com/frmdstryr/enaml-web/blob/master/docs/data-binding.gif?raw=true)

Each node as a unique identifier and can be modified using change events. An
example of this is in the examples folder.

You can also have the client trigger events on the server and have the server
trigger JS events on the client.

To use:
1. Include enaml.js in your page
2. Observe the `modified` event of an Html node and pass these changes to the
client via websockets.
3. Enamljs will send events back to the server, update the dom accordingly.


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

![Rendered Form](https://ibin.co/3Je5OwatJAGz.png)


### Database ORM with Atom

For working with a database using atom see [atom-db](https://github.com/codelv/atom-db)


#### Raw, Markdown, and Code nodes

The`Raw` node parses text into dom nodes (using lxml's html parser). Similarly
`Markdown` and `Code` nodes parse markdown and highlight code respectively.

For example, you can use wagtal's richtext tag to render to a dom via:

```python

from web.components.api import *
from web.core.api import *
from wagtail.core.templatetags.wagtailcore_tags import richtext
from myapp.views.base import Page

enamldef BlogPage(Page):
    body.cls = 'template-blogpage'
    Block:
        block = parent.content
        Raw:
            source << richtext(page.body)

```

This let's you use web wysiwyg editors to insert content into the dom.


#### Block node

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

#### Custom Components

With enaml you can easily create reusable components and share them through
the views as you would any python class using regular python imports.

For instance, to create a
[materalize breadcrumbs component](http://materializecss.com/breadcrumbs.html)
that automatically follows the current request path, simply include the required
css/scripts in your base template, define the component as shown below:

```python

from web.components.api import *
from web.core.api import Looper

enamldef Breadcrumbs(Nav): nav:
    attr path # ex. pass in a tornado request.path
    attr color = ""
    attr breadcrumbs << path[1:-1].split("/")
    tag = 'nav'
    Div:
        cls = 'nav-wrapper {}'.format(nav.color)
        Div:
            cls = 'container'
            Div:
                cls = 'col s12'
                Looper:
                    iterable << breadcrumbs
                    A:
                        href = "/{}/".format("/".join(breadcrumbs[:loop_index+1]))
                        cls = "breadcrumb"
                        text = loop_item.title()
```

then use it it as follows

```python

# in your template add
Breadcrumbs:
    path << request.path

```


### Gotachas

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

