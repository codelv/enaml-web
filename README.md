# Enaml Web Components #

Build websites with server side web components constructed using [enaml](https://github.com/nucleic/enaml) views and [lxml](http://lxml.de/) elements.   

### Websites using this

- [www.codelv.com](https://www.codelv.com/) - Built entirely using enaml-web (and cyclone)

If you made one, let me know!


### Features ###

1. Automatic form generation and population based on an Atom object similar to the django admin.
2. Inherently secure. Inputs, attributes, and tags are built into an xml DOM and thus always escaped.
3. Python removes the need for closing tags so you never forget them.
4. Reuse template tags from django/jinja2, etc... directly from code
5. Easily build extendable and reusable model based web components by linking a css framework like Bootstrap, Materialize, etc.. 
6. Web components are rendered server side which translates to fast client side rendering 
7. SEO friendly, everything is loaded like HTTP 1.0.
8. Use whatever JS you like
9. Client server data binding using websockets (optional)
10. Render markdown (with code highlighting) with python-markdown
11. Code highlighting with pygments
12. Auto reloading when you make a change in dev mode (like django's)


Binding:
![Data binding](https://github.com/frmdstryr/enaml-web/blob/master/docs/data-binding.gif?raw=true)

Form:
![Rendered Form](https://ibin.co/3Je5OwatJAGz.png)

### Usage ###


####  Setup ####

 A page is defined as an enaml view directly in python as shown below. Simply replace html tags with the enaml component (eg. the capitalized tag name). 

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

The enaml view then generates the an xml tree (using lxml) based on the models and variables passed to the template. Finally, the toolkit implementation renders the lxml and writes the response.  


```python

import enaml
import tornado.web

class IndexHandler(tornado.web.RequestHandler):
    view = None # Set statically so it's only loaded once
    def get(self):
        if self.view is None:
            with enaml.imports():
                from index import Index
            self.__class__.view = Index()
        self.write(self.view.render()) 


```

Next simply pass the app for your server to the corresponding implemenation of the enaml application.

```python

import tornado.web

class Application(tornado.web.Application,object):
    def __init__(self):
        super(Application, self).__init__([
                (r'/',IndexHandler) 
           ],
            xheaders=False
        )
        
if __name__ == "__main__":
    from web.impl.tornado_app import TornadoApplication
    app = TornadoApplication(port=8888, app=Application())
    app.start()

```

#### Templates ####

You can define a base template, then overwrite parts using the `Block` node.


In a file `templates.enaml` put:

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

Then you can _extend_ the template and override the block content

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

This is very helpful when creating reusuable components.

#### Components ####

Probably the best part, with enaml you can easily create reusable components and share them through the views as you would any python class.

For instance, to create a [materalize breadcrumbs component](http://materializecss.com/breadcrumbs.html) that automatically follows the current request path, simply include the required css/scripts in your base template, define the component as shown below:

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

#### Data models ####

Forms can automatically be generated and populated using the  `AutoForm` component. Just define an Atom model such as

```python

from atom.api import Atom, Unicode, Bool, Enum

class Message(Atom):
    name = Unicode()
    email = Unicode()
    message = Unicode()
    options = Enum("Email","Phone","Text")
    sign_up = Bool(True)


``` 

Next use the `AutoForm` node and pass in either a new or populated instance of the model to render the form.

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
### Data binding ###

_Note: Ths is a WIP and will definitely change _

Any `Tag` instance now supports updating attributes with the bound values when the models change on the _server_  via websockets.  You can also have the client trigger events on the serve and have the server trigger JS events on the client.  

Implementation details soon to follow. . as many things are changing. For now see the data_binding example.

To use:
1. Include enaml.js in your page
2. Use a websocket handle and send events 


#### Raw node ####

The`Raw` node parses text into dom nodes (using lxml's html parser). This means you can use 
enaml-web along side of existing template engines like jinja2 and any systems that use 
them (ex django). 

Also, since enaml is just python, you can use other "template tags" from other libraries  directly 
by calling the function the tag maps to. For instance wagtail's richtext tag:


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

This let's you use web wysiwyg editors to insert content into the etree.
 

### Gotachas ###

##### Text and tail nodes #####

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

Notice how `tail` is set on the `A` NOT the `P`.  See [lxml etree documentation](http://lxml.de/tutorial.html#elements-contain-text) for more details. 

##### Tag attribute #####

In the current implementation the xml tag used is the lowercase of the class name. When you subclass a component you must explicity set the tag attribute to the desired tag name. For example:

```python

enamldef Icon(I):
    tag = 'i' # Force tag to be 'i' instead of 'icon' since 'icon' is not a valid html element
    cls = 'material-icons'

```

### How it works ###

1.Each enaml declaration generates an lxml etree element populated with attributes and children specific to the component declaration.  
2. Enaml's powerful observer engine handles updating attributes and node structure when models change.  
3. The lxml tree is then simply rendered to a string to be used in the request handler.

### Servers ###

Currently supports the following webservers:

1. Tornado
2. Twisted
3. Cyclone
4. Sanic
5. aiohttp

But you can uses it as a templating engine for any server (ex django, flask, etc..) or just 
use it as a static site generator.












 



