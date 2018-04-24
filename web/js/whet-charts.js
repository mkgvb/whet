var WhetCharts = {};
$(document).ready(function () {

    WhetCharts.temperature = make_doughnut_chart(
        document.getElementById('chart-doughnut-temperature'),
        'Temperature',
        '#457345',
        0, 100)

    WhetCharts.fan = make_doughnut_chart(
        document.getElementById('chart-doughnut-fans'),
        'Fan Speed %',
        '#457345',
        0, 100)

    WhetCharts.watts = make_doughnut_chart(
        document.getElementById('chart-doughnut-watts'),
        'Power Usage',
        '#457345',
        0, 100)

    function make_doughnut_chart(ctx, title_in, color, init_value_in = 0, init_max_in = 100) {

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [title_in, ''],
                datasets: [
                    {
                        data: [init_value_in, init_max_in],
                        backgroundColor: [color, "rgb(179, 179, 179)"]
                    }
                ]
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: title_in
                },
                legend: {
                    display: false
                },
                tooltips: {
                    enabled: true
                },
                elements: {
                    center: {
                        text: init_value_in,
                        color: '#000000', // Default is #000000
                        fontStyle: 'Arial', // Default is Arial
                        sidePadding: 35 // Defualt is 20 (as a percentage)
                    }
                }
                //     rotation: -1.0 * Math.PI, // start angle in radians
                //     circumference: Math.PI, // sweep angle in radians
            }
        });
    }


});

Chart.pluginService.register({
    beforeDraw: function (chart) {
        if (chart.config.options.elements.center) {
    //Get ctx from string
    var ctx = chart.chart.ctx;
    
            //Get options from the center object in options
    var centerConfig = chart.config.options.elements.center;
      var fontStyle = centerConfig.fontStyle || 'Arial';
            var txt = centerConfig.text;
    var color = centerConfig.color || '#000';
    var sidePadding = centerConfig.sidePadding || 20;
    var sidePaddingCalculated = (sidePadding/100) * (chart.innerRadius * 2)
    //Start with a base font of 30px
    ctx.font = "30px " + fontStyle;
    
            //Get the width of the string and also the width of the element minus 10 to give it 5px side padding
    var stringWidth = ctx.measureText(txt).width;
    var elementWidth = (chart.innerRadius * 2) - sidePaddingCalculated;

    // Find out how much the font can grow in width.
    var widthRatio = elementWidth / stringWidth;
    var newFontSize = Math.floor(30 * widthRatio);
    var elementHeight = (chart.innerRadius * 2);

    // Pick a new font size so it will not be larger than the height of label.
    var fontSizeToUse = Math.min(newFontSize, elementHeight);

            //Set font settings to draw it correctly.
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    var centerX = ((chart.chartArea.left + chart.chartArea.right) / 2);
    var centerY = ((chart.chartArea.top + chart.chartArea.bottom) / 2);
    ctx.font = fontSizeToUse+"px " + fontStyle;
    ctx.fillStyle = color;
    
    //Draw text in center
    ctx.fillText(txt, centerX, centerY);
        }
    }
});




function update_chart_doughnut_fans(data_in) {
    // var value = Math.round(Math.random() * 100); //delete me
    var value = data_in[0].value
    var chart = WhetCharts.fan;
    var offset = 100 - value

    chart.data.datasets[0].data = [value, offset]
    chart.options.elements.center.text = value + "%"
    //add
    // chart.data.datasets.forEach((dataset) => {
    //     console.log(dataset)
    //     dataset.data.pop()
    //     dataset.data.push([66, 10])
    //     console.log(dataset)
    //     console.log('done')
    // });

    chart.update()
}

function update_chart_doughnut_watts(data_in) {
    var max_value = 200;
    // var value = Math.round(Math.random() * 100); //delete me
    var value = Math.round(data_in)
    var chart = WhetCharts.watts
    var offset = max_value - value

    chart.data.datasets[0].data = [value, offset]
    chart.options.elements.center.text = value + "w"
    //add
    // chart.data.datasets.forEach((dataset) => {
    //     console.log(dataset)
    //     dataset.data.pop()
    //     dataset.data.push([66, 10])
    //     console.log(dataset)
    //     console.log('done')
    // });

    chart.update()
}