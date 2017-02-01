# Enaml for Web #

A web toolkit built with twisted as the server and material widgets using lxml. 

NOTE: This does NOT work at all, just testing out the concept at the moment.

## Concept ##

1. Define an Enaml view to layout a page with a model as you do in Qt apps 
2. Implement [material components](https://getmdl.io/components/index.html) as Enaml widgets
    a. Widgets are lxml nodes 
3. A twisted resource links the request to the view (somehow)
4. Somehow do server to client data binding and the opposite via websockets (why I chose Twisted)


### Why? ###

The whole site will be rendered once. After that the model(s) simply update the nodes that change which should make it fast.



