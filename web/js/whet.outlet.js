
conn.onmessage = function (e) {

    var eparsed = JSON.parse(e.data);

    if (eparsed.outlet_schedule != null) {
        edit(eparsed.outlet_schedule);

    }

};

$("#submit-button").click(function (event) {
    console.log("BUTTON CLICK");
    $(this).removeClass("btn-primary")
    if (is_valid_submission)
    {
        conn.send(JSON.stringify({ update: { outlet_schedule: editor_data } }));
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
        disable_array_add: false,
        disable_array_delete: false,
        disable_array_reorder: false,
        disable_collapse: true,
        disable_edit_json: false,
        disable_properties: true,

        schema: {
            "title": "Outlets",
            "type": "array",
            "format": "tabs",
            "uniqueItems": true,
            "items": {
                "type": "object",
                "headerTemplate": "{{ self.id }} - {{self.name}}",
                "format": "grid",
                "properties": {
                    "id": {
                        "type": "integer",
                        "default": 1,
                        "minimum": 1,
                        "maximum": 4,
                        "options": { "hidden": true }
                    },
                    "name": {
                        "type": "string",
                    },
                    "active": {
                        "title": "schedule active",
                        "type": "boolean",
                    },
                    "pulse": {
                        "title": "pulse active",
                        "type": "boolean",
                        "default": false
                    },
                    "schedule": {
                        "type": "array",
                        "format": "table",
                        "title": "Schedule",
                        "items": {
                            "type": "object",
                            "title": "Event",
                            "properties": {
                                "start": {
                                    "type": "string",
                                    "format":"time",
                                    "readonly": false
                                },
                                "end": {
                                    "type": "string",
                                    "format":"time",
                                    "step":1,
                                    "readonly": false
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
            //conn.send(JSON.stringify({ update: { outlet_schedule: data } }));
        }
    });

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
            
        }
    });


}

$(document).ready(function () {


});


