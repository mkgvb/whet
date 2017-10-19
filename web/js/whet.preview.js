$(function () {
    var channels = [];
    var lightSchedule = {};
    var settings = {};
    var conn = null;

    if (conn == null)
        connect();

    function connect() {
        disconnect();

        conn = new SockJS('http://' + window.location.host + '/chat', 0);

        conn.onopen = function () {
            conn.send('{"request":"light_schedule"}');
            update_ui();
        };
        conn.onmessage = function (e) {

            var eparsed = JSON.parse(e.data);

            if (eparsed.channel != null) {
                draw_pwmChannel(eparsed.channel);
            }

            if (eparsed.channels != null) {
                edit(eparsed.channels);

            }

        };
        conn.onclose = function () {
            log('Disconnected.');
            conn = null;
            update_ui();
        };
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



    function edit(eChannels) {
        // Set default options
        JSONEditor.defaults.options.theme = 'bootstrap3';

        // Initialize the editor
        var editor = new JSONEditor(document.getElementById("editor_holder"), {
            disable_array_add: true,
            disable_array_delete: true,
            disable_array_reorder: true,
            disable_collapse: true,
            disable_edit_json: true,
            disable_properties: true,

            schema: {
                "title": "Preview",
                "type": "array",
                "format": "tabs",
                "items": {
                    "type": "object",
                    "headerTemplate": "Channel - {{ self.id }}",
                    "format": "grid",
                    "properties": {
                        "preview": {
                            "headerTemplate": "{{ self.value }}",
                            "properties": {
                                "active": {
                                    "type": "boolean",
                                    "format": "checkbox",
                                    "default": false,
                                },
                                "value": {
                                    "type": "number",
                                    "format": "range",
                                    "default": 500,
                                    "minimum": 0,
                                    "maximum": 4095
                                }
                            }
                        },
                        "id": {
                            "type": "integer",
                            "default": 0,
                            "minimum": 0,
                            "maximum": 16,
                            "options": { "hidden": true }
                        },
                        "color": {
                            "type": "string",
                            "format": "color",
                            "title": "Color",
                            "default": "#ffffff",
                            "options": { "hidden": true }
                        },
                        "schedule": {
                            "type": "array",
                            "format": "table",
                            "title": "Schedule",
                            "uniqueItems": true,
                            "options": { "hidden": true },
                            "items": {
                                "type": "object",
                                "title": "Event",
                                "properties": {
                                    "hour": {
                                        "type": "integer",
                                        "readonly": true
                                    },
                                    "percent": {
                                        "type": "integer",
                                        "default": 0,
                                        "minimum": 0,
                                        "maximum": 100,
                                    }
                                }
                            }
                        }
                    }
                }
            }

        });
        editor.options.show_errors = "always";
        var j = editor.getEditor('root');
        //editor.getEditor('root0.schedule').disable();

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
            var errors = editor.validate();
            if (errors.length == 0) {
                var data = editor.getValue();
                conn.send( JSON.stringify({update: { channels: data}}));
            }
        });
    }


});
