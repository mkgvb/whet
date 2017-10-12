$(function () {
    var channels = [];
    var lightSchedule = {};
    var settings = {};
    var conn = null;

    edit();

    function edit(){
        // Set default options
        JSONEditor.defaults.options.theme = 'bootstrap3';

        // Initialize the editor
        var editor = new JSONEditor(document.getElementById("editor_holder"),{
        schema: {
            "title": "Channel",
            "type": "object",
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
        });

        // Set the value
        editor.setValue({
            name: "John Smith"
        });

        // Get the value
        var data = editor.getValue();
        console.log(data.name); // "John Smith"

        // Validate
        var errors = editor.validate();
        if(errors.length) {
        // Not valid
        }

        // Listen for changes
        editor.on("change",  function() {
        // Do something...
        });
            }


});