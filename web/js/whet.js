
var lightSchedule = {};
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
    console.log(window.location);
    conn = new SockJS(window.location.origin + '/chat', 0);   //last param is transport, 0 is websocket
    log('Connecting...');
    conn.onopen = function () {
        log('Connected.');
        conn.send(JSON.stringify({ request: "light_schedule" }));
        conn.send(JSON.stringify({ request: "settings" }));
        conn.send(JSON.stringify({ request: "outlet_schedule" }));
        update_ui();
    };
    conn.onmessage = function (e) {

        var eparsed = JSON.parse(e.data);
        log('Received: ' + JSON.stringify(eparsed, null, 2));

        if (eparsed.type == "user")
            log("User did something");

        if (eparsed.status != null) {
            draw_pwmChannel(eparsed.status);
        }



        if (eparsed.channels != null) {
            lightSchedule = eparsed.channels;
            //draw_lightSchedule_Table(lightSchedule);
            draw_lightSchedule_graph(lightSchedule);
        }

        if (eparsed.outlet_status != null) {
            draw_outletStatus(eparsed.outlet_status)
        }

        if (eparsed.temperature != null) {
            draw_temperature(eparsed.temperature)
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
$('#chatform').submit(function () {
    var text = $('#text').val();
    log('Sending: ' + text);
    conn.send(text);
    $('#text').val('').focus();
    return false;
});

Handlebars.getTemplate = function (name) {
    if (Handlebars.templates === undefined || Handlebars.templates[name] === undefined) {
        $.ajax({
            url: '/web/templates/' + name + '.handlebars',
            success: function (data) {
                if (Handlebars.templates === undefined) {
                    Handlebars.templates = {};
                }
                Handlebars.templates[name] = Handlebars.compile(data);
            },
            async: false
        });
    }
    return Handlebars.templates[name];
};

draw_top();
function draw_top() {
    // Compile the template
    var theTemplate = Handlebars.getTemplate('top');

    // Pass our data to the template
    var theCompiledHtml = theTemplate();

    // Add the compiled html to the page
    $('#top').replaceWith(theCompiledHtml);
}

draw_nav();
function draw_nav() {
    var content = $(".body");

    // Compile the template
    var theTemplate = Handlebars.getTemplate('navbar');

    //get the name of the current page without .html
    var h = location.pathname.split("/").slice(-1)[0].split(".")[0].toLowerCase();
    console.log(h);
    var info = {};
    info[h] = true;

    // Pass our data to the template
    var theCompiledHtml = theTemplate(info);

    // Add the compiled html to the page
    $('.navbar').replaceWith(theCompiledHtml);
}

draw_ws_messages();
function draw_ws_messages() {
    var content = $("#ws-messages");
    var theTemplate = Handlebars.getTemplate('ws-messages');
    var theCompiledHtml = theTemplate();
    content.html(theCompiledHtml);
}

function draw_temperature(temperature) {
    var value = temperature[0].value;
    var content = $("#temperature-status");
    document.getElementById('temperature-status').innerHTML = value + '&#8457;';
}


function draw_pwmChannel(c_obj) {
    var content = $("#channel-statuses");
    // Grab the template script
    var theTemplateScript = $("#channel-status-template").html();

    // Compile the template
    var theTemplate = Handlebars.getTemplate('channel-status');

    c_obj.forEach(function (val) {

        // Pass our data to the template
        var theCompiledHtml = theTemplate(val);

        if (content.find("#channel_" + val.c_id).length === 0) {
            content.append(theCompiledHtml);
        }

        // Add the compiled html to the page
        $('#channel_' + val.c_id).replaceWith(theCompiledHtml);

    }, this);


    //sort the children
    var listitems = content.children("div");
    listitems.sort(function (a, b) {
        var compA = $(a).attr('id').toUpperCase();
        var compB = $(b).attr('id').toUpperCase();
        //console.log((compA < compB) ? -1 : (compA > compB) ? 1 : 0);
        return (compA < compB) ? -1 : (compA > compB) ? 1 : 0;
    })
    $(content).append(listitems);
}

function draw_outletStatus(c_obj) {
    var content = $("#outlet-statuses");
    // Grab the template script
    var theTemplateScript = $("#outlet-status-template").html();

    // Compile the template
    var theTemplate = Handlebars.getTemplate('outlet-status');


    c_obj.outlet_schedule.forEach(function (val) {

        // Pass our data to the template
        var theCompiledHtml = theTemplate(val);

        if (content.find("#outlet_status_" + val.id).length === 0) {
            content.append(theCompiledHtml);
        }

        // Add the compiled html to the page
        $('#outlet_status_' + val.id).replaceWith(theCompiledHtml);

    }, this);

}

function hexToRgb(hex, alpha) {
    if (hex == undefined)
        hex = '#00000';
    hex = hex.replace('#', '');
    var r = parseInt(hex.length == 3 ? hex.slice(0, 1).repeat(2) : hex.slice(0, 2), 16);
    var g = parseInt(hex.length == 3 ? hex.slice(1, 2).repeat(2) : hex.slice(2, 4), 16);
    var b = parseInt(hex.length == 3 ? hex.slice(2, 3).repeat(2) : hex.slice(4, 6), 16);
    if (alpha) {
        return 'rgba(' + r + ', ' + g + ', ' + b + ', ' + alpha + ')';
    }
    else {
        return 'rgb(' + r + ', ' + g + ', ' + b + ')';
    }
}

function draw_lightSchedule_graph(channels) {
    var graphData = [];
    var graphLabels = [];

    //determine unique labels (hours)
    //have to loop through every schedule event on all channels to know this
    channels.forEach(function (item, index, array) {
        item.schedule.forEach(function (item_n, index_n, array_n) {
            if (!graphLabels.includes(item_n.hour)) {
                graphLabels[item_n.hour] = item_n.hour;
            }
        });
    });

    sorted_labels = [];
    graphLabels.forEach(function(item_n, index_n, array_n) { return sorted_labels.push(item_n) });

    //determine value for channels based on unique graph labels, assume 0 if not in array
    channels.forEach(function (item, index, array) {
        var s = {};
        s.label = item.alias;
        s.data = [];

        sorted_labels.forEach(function (item_n, index_n,array_n) {
            if (item.schedule.find(x => x.hour === item_n) != undefined)
                s.data.push(item.schedule.find( x => x.hour === item_n).percent);
            else
                s.data.push(0);
        })

        s.backgroundColor = [hexToRgb(item.color, 0.2)];
        s.borderColor = [hexToRgb(item.color, 0.2)];
        s.borderWidth = 1;
        s.lineTension = .4;
        graphData.push(s);

    });



    var ctx = document.getElementById("myChart").getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sorted_labels,
            datasets: graphData
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        callback: function (dataLabel, index) {
                            // Hide the label of every 2nd dataset. return null to hide the grid line too
                            // return index % 2 === 0 ? dataLabel + '%' : null;
                            return dataLabel + '%';
                        }
                    }
                }],
                xAxes: [{
                    display: true,
                    ticks: {
                        callback: function (dataLabel, index) {
                            // Hide the label of every 2nd dataset. return null to hide the grid line too
                            //return index % 2 === 0 ? dataLabel + ':00' : '';
                            return dataLabel + ':00';
                        }
                    }
                }]
            }
        }
    });
}