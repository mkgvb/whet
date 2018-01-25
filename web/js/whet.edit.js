
conn.onopen = function () {
    conn.send(JSON.stringify({ request: "light_schedule" }));
    update_ui();
};
conn.onmessage = function (e) {

    var eparsed = JSON.parse(e.data);

    if (eparsed.channels != null) {
        edit(eparsed.channels);

    }

};

$("#submit-button").click(function (event) {
    console.log("BUTTON CLICK");
    $(this).removeClass("btn-primary")
    if (is_valid_submission)
    {
        conn.send(JSON.stringify({ update: { channels: editor_data } }));
        $(this).addClass("btn-success");
    }
    else
        $(this).addClass("btn-danger");
    

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
        disable_properties: true,
        schema: {
            "title": "Channels",
            "type": "array",
            "format": "tabs",
            "items": {
                "type": "object",
                "headerTemplate": "Channel - {{ self.id }}",
                "format": "grid",
                "properties": {
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
                        "default": "#ffffff"
                    },
                    "lightning": {
                        "type": "boolean",
                        "title": "enable lightning",
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
                    },
                    "preview": {
                        "options": { "hidden": true }
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
        $("#submit-button").removeClass()
        $("#submit-button").addClass("btn btn-primary")
        console.log(JSON.stringify({ update: { outlet_schedule: data } }));
        if (errors.length == 0) {
            is_valid_submission = true;
            editor_data = editor.getValue();
            draw_lightSchedule_graph(data);
            
            
        }
    });
}