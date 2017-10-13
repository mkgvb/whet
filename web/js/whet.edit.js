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
                draw_lightSchedule_graph(lightSchedule);
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

    function draw_lightSchedule_graph(channels) {
        var ds0 = [];
        var ds1 = [];
        var ds2 = [];
        var ds3 = [];
        var labels = []
        for (i = 0; i < 24; i++) {
            ds0.push(channels[0].schedule[i].percent);
            ds1.push(channels[1].schedule[i].percent);
            ds2.push(channels[2].schedule[i].percent);
            ds3.push(channels[3].schedule[i].percent);
            labels.push(channels[0].schedule[i].hour);
        }

        var ctx = document.getElementById("myChart").getContext('2d');
        var myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Channel 0',
                        data: ds0,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.2)',
                            'rgba(54, 162, 235, 0.2)',
                            'rgba(255, 206, 86, 0.2)',
                            'rgba(75, 192, 192, 0.2)',
                            'rgba(153, 102, 255, 0.2)',
                            'rgba(255, 159, 64, 0.2)'
                        ],
                        borderColor: [
                            'rgba(255,99,132,1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)'
                        ],
                        borderWidth: 1
                    },
                    {
                        label: 'Channel 1',
                        data: ds1,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.2)',
                            'rgba(255, 206, 86, 0.2)',
                            'rgba(75, 192, 192, 0.2)',
                            'rgba(153, 102, 255, 0.2)',
                            'rgba(255, 159, 64, 0.2)'
                        ],
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)'
                        ],
                        borderWidth: 1
                    },
                    {
                        label: 'Channel 2',
                        data: ds2,
                        backgroundColor: [
                            'rgba(255, 206, 86, 0.2)',
                            'rgba(75, 192, 192, 0.2)',
                            'rgba(153, 102, 255, 0.2)',
                            'rgba(255, 159, 64, 0.2)'
                        ],
                        borderColor: [
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)'
                        ],
                        borderWidth: 1
                    },
                    {
                        label: 'Channel 3',
                        data: ds3,
                        backgroundColor: [
                            'rgba(75, 192, 192, 0.2)',
                            'rgba(153, 102, 255, 0.2)',
                            'rgba(255, 159, 64, 0.2)'
                        ],
                        borderColor: [
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)'
                        ],
                        borderWidth: 1
                    }

                ]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        });
    }







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
                    "format": "grid",
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
            var data = editor.getValue();
            draw_lightSchedule_graph(data)
            conn.send('{"update":{"channels":' + JSON.stringify(data) + "}}");
        });
    }


});
