conn.onmessage = function (e) {

    var eparsed = JSON.parse(e.data);

    if (eparsed.status != null) {
        draw_pwmChannel(eparsed.status);
    }

    if (eparsed.channels != null) {
        edit(eparsed.channels);

    }

};


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
                    "color": {
                        "type": "string",
                        "format": "color",
                        "title": "Color",
                        "default": "#ffffff",
                        "readonly":true
                    },
                    "preview": {
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
            conn.send(JSON.stringify({ update: { channels: data } }));
        }
    });

    //bootstrap switches
    //$("input[type='checkbox']").bootstrapSwitch();

    //creates active output for range sliders 
    $("input[type='range']").each(
        function (index) {
            var in_id_string = "in" + index;
            var out_id_string = "out" + index;
            console.log("range slider");
            $(this).attr('id', in_id_string);
            $(this).attr("oninput", out_id_string + ".value=" + in_id_string + ".value");
            $(this).before("<output id='" + out_id_string + "'>" + $(this).val() + "</output>");
        });
}

$(document).ready(function () {


});


