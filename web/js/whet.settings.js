var editor_data;
var is_valid_submission = false;


$("#submit-button").click(function (event) {
    console.log("BUTTON CLICK");
    $(this).removeClass("btn-primary")
    if (is_valid_submission)
    {
        conn.send(JSON.stringify({ update: { settings: editor_data } }));
        $(this).addClass("btn-success");
    }
    else
        $(this).addClass("btn-danger");
    

});

conn.onmessage = function (e) {
    var eparsed = JSON.parse(e.data);

    if (eparsed.settings != null) {
        s = eparsed.settings;
        //draw_settings(s);
        settings_editor(s);
    }
};

function draw_settings(settings) {

    var content = $("#settings-content");
    content.empty();

    for (var property in settings) {
        if (settings.hasOwnProperty(property)) {

            var row = document.createElement('div');
            row.className = 'form-group row';

            var label = document.createElement('label');
            label.className = 'col-3 col-form-label';
            label.innerText = property.replace(/_/g, " ");
            label.setAttribute('for', property);

            var input = document.createElement('input');
            input.className = 'form-control';

            var input_wrap = document.createElement('div');
            input_wrap.className = 'col-2';
            input_wrap.appendChild(input);

            if (typeof settings[property] === "string") {
                input.type = "textbox";
                input.name = property;
                input.value = settings[property];
            }

            if (typeof settings[property] === "number") {
                input.type = "number";
                input.name = property;
                input.value = settings[property];
            }

            if (typeof settings[property] === "boolean") {
                input.type = "checkbox";
                input.name = property;
                input.id = property;
                input.checked = settings[property];
                input.value = settings[property];
                $(input).bootstrapSwitch();

            }

            row.appendChild(label);
            row.appendChild(input_wrap);
            content.append(row);
        }
    }
}

function settings_editor(eSettings) {
    // Set default options
    JSONEditor.defaults.options.theme = 'bootstrap3';

    // Initialize the editor
    var editor = new JSONEditor(document.getElementById("settings-editor"), {
        disable_array_add: true,
        disable_array_delete: true,
        disable_array_reorder: true,
        disable_collapse: true,
        disable_edit_json: true,
        disable_properties: true,

        schema: {
            "title": "Settings",
            "type": "object",
            "properties": {
                "weather": {
                    "type":"string",
                    "enum": ["normal","storm","cloudy"]
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
        eSettings

    );

    // Get the value
    var data = editor.getValue();
    

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
        console.log(JSON.stringify({ update: { settings: data } }));
        if (errors.length == 0) {
            is_valid_submission = true;
            editor_data = editor.getValue();
            
        }
    });
}