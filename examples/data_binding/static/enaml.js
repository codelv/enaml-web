(function($){
  $(function(){
    // constructor
    var Enaml = (function(){
        function Enaml() {
            this.ws = null;
            this.connect();
            this.observe();
        };
        
        Enaml.prototype.observe = function() {
            var Enaml = this;
            $('[data-onclick="1"]').on('click',function(e){ // Should i just do everthing?
                e.preventDefault();
                Enaml.sendEvent({'ref':$(this).attr('ref'),'type':'event','name':'on_click'});
            });
            $(":checkbox").on('change',function(){ // Should i just do everthing?
              Enaml.sendEvent({
                'ref':$(this).attr('ref'),
                'type':'update',
                'name':'checked',
                'value':($(this).prop('checked'))?'checked':'',
              });
            });
            $("select").on('change',function(){ // Should i just do everthing?
                Enaml.sendEvent({
                  'ref':$(this).attr('ref'),
                  'type':'update',
                  'name':'value',
                  'value':$(this).val(),
                });
              });
            $('input').on('input',function(){ // Should i just do everthing?
                Enaml.sendEvent({
                    'ref':$(this).attr('ref'),
                    'type':'update',
                    'name':'value',
                    'value':$(this).val()
                });
            });
        };
        
        Enaml.prototype.unobserve = function() {
            var Enaml = this;
            $('[data-onclick="1"]').off('click');
            //$('[data-onclick="1"]').off('click');
        };
    
       // Define Enaml
        Enaml.prototype.onOpen = function(event) {
            console.log("On open!");
        };
        
        Enaml.prototype.onMessage = function(event) {
            console.log(event);
            var change = JSON.parse(event.data);
            var $tag = $('[ref="'+change.ref+'"]');
            if (change.type==="refresh") {
                this.unobserve();
                $tag.html(change.value);
                this.observe();
            } else if (change.type==="trigger") {
                $tag.trigger(change.value);
            } else if (change.type==="update") {
                if (change.name==="text") {
                    $tag.contents().get(0).nodeValue = change.value;
               // TODO: handle tail
                } else if (change.name==="attrs") {
                    $.map(change.value,function(v,k){
                        $tag.prop(k,v);
                    });
                } else {
                    $tag.prop(change.name,change.value);
                }
                // Special hack for materialize...
                if ($tag.prop('tagName')==='SELECT') {
                    $tag.material_select();
                }
            }
        };
        
        Enaml.prototype.connect = function() {
            var Enaml = this;
            var url = "ws://localhost:8888"+window.location.pathname;
            console.log("Connecting to "+url);
            this.ws = new WebSocket(url);
            this.ws.onopen = function(e){
                Enaml.onOpen(e);
            };
            this.ws.onmessage = function(e){
                Enaml.onMessage(e);
            };
            this.ws.onclose = function(e){
                Enaml.onClose(e);
            };
        };
        
        Enaml.prototype.sendEvent = function(event) {
            event.id = $('html').attr('id');
            console.log(event);
            this.ws.send(JSON.stringify(event));
        };
        
        Enaml.prototype.onClose = function(event) {
            console.log("Connection is closed...");
            this.connect();
        };
        return Enaml;
    })();
    
    window.Enaml = new Enaml();

  }); // end of document ready
})(jQuery); // end of jQuery name space