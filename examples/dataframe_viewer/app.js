function initViewer(ref) {
    var ws = new WebSocket("ws://localhost:8888/websocket/?ref="+ref);
    ws.onopen = function(evt) {
        console.log("Connected!");
    };

    ws.onmessage = function(evt) {
        var change = JSON.parse(evt.data);
        console.log(change);
        var $tag = $('[ref="'+change.ref+'"]');
        change.object = $tag;

        if (change.type === 'refresh') {
            $tag.html(change.value);
        } else if (change.type === 'trigger') {
            $tag.trigger(change.value);
        } else if (change.type === 'added') {
            $tag.append($(change.value));
        } else if (change.type === 'removed') {
            $tag.find('[ref="'+change.value+'"]').remove();
        } else if (change.type === 'update') {
            if (change.name==="text") {
                var node = $tag.contents().get(0);
                if (!node) {
                    node = document.createTextNode("");
                    $tag.append(node);
                }
                node.nodeValue = change.value;
            } else if (change.name==="attrs") {
                $.map(change.value,function(v,k){
                    $tag.prop(k,v);
                });
            } else {
                if (change.name==="cls") {
                    change.name = "class";
                }
                $tag.prop(change.name,change.value);
            }
        } else {
            console.log("Unknown change type");
        }
    };

    ws.onclose = function(evt) {
        console.log("Disconnected!");
    };

    function sendEvent(change) {
        console.log(change);
        ws.send(JSON.stringify(change));
    };

    function sendNodeValue(){
        sendEvent({
            'ref':$(this).attr('ref'),
            'type':'update',
            'name':'value',
            'value':$(this).val(),
        });
    };

    $(document).on('click', '[clickable]',function(e){
        e.preventDefault();
        sendEvent({
            'ref':$(this).attr('ref'),
            'type':'event',
            'name':'clicked'
        });
    });
    $(document).on('change', ":checkbox", function(){
        sendEvent({
        'ref':$(this).attr('ref'),
        'type':'update',
        'name':'checked',
        'value':($(this).prop('checked'))?'checked':'',
        });
    });
    $(document).on('change', "select", sendNodeValue);
    $(document).on('input', 'input', sendNodeValue);
    $(document).on('change', 'textarea', function() {
        sendEvent({
            'ref':$(this).attr('ref'),
            'type':'update',
            'name':'text',
            'value':$(this).val(),
        });
    });

    return ws;
}
