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

