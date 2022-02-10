# 0.11.0

- Move to python 3 only syntax and add typing annotations
- Reformat with black
- Add `dragstart` and `dragover` events to `Tag`
- Slightly speed up init_widget and use lru cache for determining attributes
- Use lru cache for proxy resolve class
- Remove unused init functions
- Remove logger and database from WebApplication, if you want those add them
in a subclass.
- Change id generator to use a shorter (but slightly slower) version



# 0.10.2

Make markdown source modified event return the rendered value

> This is the last version that works on python 2.7

# 0.10.1

Fix bug where Block with replace mode did not replace all child nodes

# 0.9.1

Allow passing keyword arguments to proxy.render and change encoding to 'unicode'
by default (tests show it's faster) and don't pretty print by default.

# 0.9.0

Remove `ref` and just use `id` instead

# 0.8.10

Add slot to support weakref on the Html tag

# 0.8.9

Change tag attribute to use `set_default` instead of lower of class name.
Rename `find` of ProxyTag to `xpath`.


# 0.8.8

Add support for moved nodes

# 0.8.7

Indicate where an added element should be inserted.

# 0.8.5

Use dict instead of sortedmap for caching (deletion is slow)

# 0.8.4

Use atomref instead of weakref

# 0.8.3

- The refs are now hex formatted to make them shorter
- Fixed double ';' when using style dict
- Add draggable and support for drag/drop events

# 0.8.2

Added optgroup

# 0.8.0

DB API was moved to an external project named `atom-db`

# 0.7.0

DB API was changed to use a `get_or_create` method that can work with caching
when restoring objets from the database. The serializer `find_object` was
renamed to `get_object_state` and takes the object created by `get_or_create`
instead of the object class.


# 0.6.2

Add option to define order when restoring state by tagging members with
a `setstate_order=<number>` to used for sorting. The default is `1000`.

# 0.6.1

Replace `Bool` fields with `Coerced(bool)` to better support numpy bools.

# 0.6.0

The `web.core.db` module refactored and made into a package and split to
support both nosql and sql.

# 0.5.0

Application wrappers have been dropped. Just use `web.core.app.WebApplication`.

In order to handle websockets now, a `modified` event was added to the root
`Html` tag. This will be triggered with the change from every child node.
Simply have your websockets observe this event for changes and
handle it accordingly.


# 0.4.4

Added ipython notebook renderer.

