$(function () {
    var channels = [];
    var lightSchedule = {};
    var settings = {};
    var conn = null;

    if (conn == null)
        connect();


    function log(msg) {
        var control = $('#log');
        control.html(control.html() + msg + '<br/>');
        control.scrollTop(control.scrollTop() + 200);
    }
    function connect() {
        disconnect();
        var transports = $('#protocols input:checked').map(function () {
            return $(this).attr('id');
        }).get();
        conn = new SockJS('http://' + window.location.host + '/chat', 0);
        log('Connecting...');
        conn.onopen = function () {
            log('Connected.');
            conn.send('{"request":"light_schedule"}');
            conn.send('{"request":"settings"}')
            update_ui();
        };
        conn.onmessage = function (e) {

            var eparsed = JSON.parse(e.data);
            log('Received: ' + JSON.stringify(eparsed, null, 2));

            if (eparsed.type == "user")
                log("User did something");

            if (eparsed.channel != null) {
            }


            if (eparsed.channels != null) {
                lightSchedule = eparsed.channels;
                edit(lightSchedule);
            }

            if (eparsed.settings != null) {
                settings = eparsed.settings;
            }

            var d = new Date();
            var n = "(" + d.getHours() + ")" + d.toLocaleTimeString();
            $("#time").text(n);





        };
        conn.onclose = function () {
            log('Disconnected.');
            conn = null;
            update_ui();
        };
    }
    function disconnect() {
        if (conn != null) {
            log('Disconnecting...');
            conn.close();
            conn = null;
            update_ui();
        }
    }
    function update_ui() {
        var msg = '';
        if (conn == null || conn.readyState != SockJS.OPEN) {
            $('#status').text('disconnected');
            $('#connect').text('Connect');
        } else {
            $('#status').text('connected (' + conn.protocol + ')');
            $('#connect').text('Disconnect');
        }
    }
    $('#connect').click(function () {
        if (conn == null) {
            connect();
        } else {
            disconnect();
        }
        update_ui();
        return false;
    });
    $('form').submit(function () {
        var text = $('#text').val();
        log('Sending: ' + text);
        conn.send(text);
        var tosend = JSON.stringify(lightSchedule);
        toSend = '{"update":' + tosend + "}";
        var skip = 0;
        conn.send(toSend);
        $('#text').val('').focus();
        return false;
    });







   

    function edit(eChannels) {
        // Set default options
        JSONEditor.defaults.options.theme = 'bootstrap3';

        // Initialize the editor
        var editor = new JSONEditor(document.getElementById("editor_holder"), {
            disable_array_add: true,
            disable_array_delete: true,
            disable_array_reorder: true,
            disable_collapse: false,
            schema: {
                "title": "Channels",
                "type": "array",
                "format": "tabs",
                "items": {
                    "type": "object",
                    "headerTemplate": "Channel - {{ self.id }}",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "default": 0,
                            "minimum": 0,
                            "maximum": 16
                        },
                        "color": {
                            "type": "string",
                            "format": "color",
                            "title": "Color",
                            "default": "#ffa500"
                        },
                        "schedule": {
                            "type": "array",
                            "format": "table",
                            "title": "Schedule",
                            "uniqueItems": true,
                            "items": {
                                "type": "object",
                                "title": "Event",
                                "properties": {
                                    "hour": {
                                        "type": "integer",
                                        "default": 0
                                    },
                                    "percent": {
                                        "type": "integer"
                                    }
                                }
                            },
                            "default": [
                                {
                                    "hour": 4,
                                    "percent": 100
                                }
                            ]
                        }
                    }
                }
            }
        });

        //startval: JSON.stringify();
        // Set the value
        editor.setValue(
            eChannels
            
        );

        
        // Get the value
        var data = editor.getValue();
        //console.log(data.name); // "John Smith"
        
        
        // Validate
        var errors = editor.validate();
        if (errors.length) {
            // Not valid
        }

        // Listen for changes
        editor.on("change", function () {
            // Do something...
        });
    }


});
