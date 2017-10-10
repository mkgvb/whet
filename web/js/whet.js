$(function () {
    var channels = [];
    var conn = null;

    if (conn == null)
        connect();


    function log(msg) {
        var control = $('#log');
        control.html(control.html() + msg + '<br/>');
        control.scrollTop(control.scrollTop() + 1000);
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
            update_ui();
        };
        conn.onmessage = function (e) {
            
            var eparsed = JSON.parse(e.data);
            log('Received: ' + JSON.stringify(eparsed, null, 2));

            if (eparsed.type == "user")
                log("User did something");

            if(eparsed.channel != null)
            {
                draw_pwmChannel(eparsed.channel);
            }

            
            if (eparsed.channels != null)
            {
                lightSchedule_Table(eparsed.channels);
            }

            if (eparsed.settings != null)
            {
                draw_settings(eparsed.settings);
            }

           




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
        $('#text').val('').focus();
        return false;
    });


    function draw_pwmChannel(settings)
    {
        var content = $("#channel-statuses");

        var row = content.find("#" + settings.c_id);
        var channel = row.find(".channel-id");
        var pwm_val = row.find('.pwm-value');
        var progress = row.find('.progress-bar');
        var progress_text = row.find(".progress-text");
        
        $(channel).text(settings.c_id);
        $(pwm_val).text(settings.cur);
        $(progress).attr("aria-valuenow",settings.percent);
        $(progress).attr("style","width:"+ settings.percent + "%");
        $(progress_text).text(settings.percent +"%");
    }

    function draw_settings(settings) {

        var content = $("#settings-content")
        content.empty();

        for (var property in settings) {
            if (settings.hasOwnProperty(property)) {

                var row = document.createElement('div');
                row.className = 'form-group row';

                var label = document.createElement('label');
                label.className = 'col-3 col-form-label';
                label.innerText = property.replace(/_/g," ");
                label.setAttribute('for', property);

                var input = document.createElement('input');
                input.className = 'form-control';
                
                var input_wrap = document.createElement('div');
                input_wrap.className = 'col-2';
                input_wrap.appendChild(input);

                if (typeof settings[property] === "number" || typeof settings[property] === "string")
                {
                    input.type = "textbox";
                    input.name = property;
                    input.value = settings[property];
                }
                if (typeof settings[property] === "boolean")
                {
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


    function lightSchedule_Table(channels) {

        var content = $("#lightSchedule-content")
        content.empty();
        content.append("<th>"+"#"+"</th>")

        for(h = 0; h < 24; h++)
        {
            content.append("<th>"+h+"</th>")
        }
        for(var i = 0; i < channels.length; i++)
        {
            var row = document.createElement('tr');
            $(row).append("<th>" + channels[i].id + "</th>");   //channel name
            content.append(row);
            
            for(var j = 0; j < channels[i].schedule.length; j++)
            {
                var column = document.createElement('td');
                column.innerText = channels[i].schedule[j].percent;
                row.appendChild(column);
            }
            

        }
    }


});