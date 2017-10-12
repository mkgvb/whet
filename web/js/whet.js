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
        conn = new SockJS('http://' + window.location.host + '/chat', transports);
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
                draw_pwmChannel(eparsed.channel);
            }


            if (eparsed.channels != null) {
                lightSchedule = eparsed.channels;
                draw_lightSchedule_Table(lightSchedule);
                draw_lightSchedule_graph(lightSchedule);
            }

            if (eparsed.settings != null) {
                settings = eparsed.settings;
                draw_settings(settings);
            }

            var d = new Date();
            var n = "(" + d.getHours() + ")" + d.toLocaleTimeString();
            $("#time").text(d);





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


    function draw_pwmChannel(c_obj) {
        var content = $("#channel-statuses");

        var row = content.find("#" + c_obj.c_id);
        var channel = row.find(".channel-id");
        var pwm_val = row.find('.pwm-value');
        var progress = row.find('.progress-bar');
        var progress_text = row.find(".progress-text");

        $(channel).text(c_obj.c_id);
        $(pwm_val).text(c_obj.cur);
        $(progress).attr("aria-valuenow", c_obj.percent);
        $(progress).attr("style", "width:" + c_obj.percent + "%");
        $(progress_text).text(c_obj.percent + "%");
    }

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

                if (typeof settings[property] === "number" || typeof settings[property] === "string") {
                    input.type = "textbox";
                    input.name = property;
                    input.value = settings[property];
                }
                if (typeof settings[property] === "boolean") {
                    input.type = "checkbox";
                    input.name = property;
                    input.id = property;
                    input.checked = settings[property];
                    $(input).bootstrapSwitch();

                }



                row.appendChild(label);
                row.appendChild(input_wrap);
                content.append(row);

                // content.append("<div class='row'>"
                // +"<div class='col col-lg-2'>"+ property + "</div>")
                // content.append(input);
                // content.append("</div> </div>")

                // var 
            }
        }
    }


    function draw_lightSchedule_Table(channels) {

        var content = $("#lightSchedule-content")
        content.empty();
        content.append("<th>" + "#" + "</th>")

        for (h = 0; h < 24; h++) {
            content.append("<th>" + h + "</th>")
        }
        for (var i = 0; i < channels.length; i++) {
            var row = document.createElement('tr');
            $(row).append("<th>" + channels[i].id + "</th>");   //channel name
            content.append(row);

            for (var j = 0; j < channels[i].schedule.length; j++) {
                var column = document.createElement('td');
                var input = document.createElement("input");
                //$(input).attr("class","form-control");
                $(input).attr("type", "number");
                // $(input).attr("size","3");
                $(input).attr("max","100");
                $(input).attr("value", channels[i].schedule[j].percent);
                column.appendChild(input);
                //column.innerText = channels[i].schedule[j].percent;
                row.appendChild(column);
            }


        }
    }
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


});