var STEP, SOURCE, METHOD, SCALE, CRATE_WINDOW;

function metric(timeseries, crate, card, channel) {
    var label;
    if (card === null)
        label = 'crate ' + crate;
    else if (channel === null)
        label = 'card ' + card;
    else
        label = 'channel ' + channel;

    return timeseries.context.metric(function(start, stop, step, callback) {
        var params = {
            name: SOURCE,
            start: start.toISOString(),
            stop: stop.toISOString(),
            now: new Date().toISOString(),
            step: Math.floor(step/1000),
            crate: crate,
            card: card,
            channel: channel,
            method: METHOD
        };

        d3.json($SCRIPT_ROOT + '/metric_hash?' + $.param(params),
            function(data) {
                if (!data)
                    return callback(new Error('unable to load data'));

                return callback(null,data.values);
            }
        );
    }, label);
}

function draw(timeseries) {
    // create a horizon from timeseries.context and draw horizons
    if (timeseries.horizon) {
        d3.select(timeseries.target).selectAll('.horizon')
        .call(timeseries.horizon.remove)
        .remove();
    }

    timeseries.horizon = timeseries.context.horizon()
        .height(20)
        .colors(SCALE.range().concat(SCALE.range()))
        .extent(SCALE.domain())
        .format(timeseries.format);

    var horizons = d3.select(timeseries.target).selectAll('.horizon')
        .data(timeseries.metrics)
      .enter().insert('div','.bottom')
          .attr('class', 'horizon')
          .call(timeseries.horizon);

    if (timeseries.click)
        horizons.on('click', timeseries.click);
}

function update_metrics(timeseries) {
    if (timeseries.context !== null)
        timeseries.context.stop();

    timeseries.context = create_context(timeseries.target, STEP);
    timeseries.metrics = [];

    if (typeof timeseries.crate === 'undefined') {
        console.log("Updating all crates");
        for (var i=0; i < 2; i++) {
            timeseries.metrics[i] = metric(timeseries, i, null, null);
        }
    } else if (typeof timeseries.card === 'undefined') {
        console.log("Updating cards for crate " + timeseries.crate);
        for (var i=0; i < 16; i++) {
            timeseries.metrics[i] = metric(timeseries, timeseries.crate, i, null);
        }
    } else {
        console.log("Updating channels for crate " + timeseries.crate + " card " + timeseries.card);
        for (var i=0; i < 16; i++) {
            timeseries.metrics[i] = metric(timeseries, timeseries.crate, timeseries.card, i);
        }
    }
}

var default_thresholds = {
    charge: [100, 5e3],
    nhit: [10, 80],
    sds: [0, 80],
    occupancy: [0.001, 0.005],
    avgs: [0,16000],
    time: [0,500]
};

function set_thresholds(lo, hi) {
    // set thresholds text area
    $('#threshold-lo').val(lo);
    $('#threshold-hi').val(hi);
}

function switch_to_crate(crate) {
    card.crate(crate);
    d3.select('#card').call(card);
    $('#card-7').after('<tr></tr>');
    $('#card-15').after('<tr></tr>');
    $('#card-23').after('<tr></tr>');

    blah.crate = crate;
    blah.state = NEEDS_UPDATE;
    channelts.crate = crate;
    channelts.state = NEEDS_UPDATE;

    $('.carousel').carousel('next');
}

function switch_to_channel(crate, card) {
    channelts.crate = crate;
    channelts.card = card;
    channelts.state = NEEDS_UPDATE;
    $('#carousel').carousel('next');
}

var ACTIVE = 0,
    PAUSED = 1,
    NEEDS_UPDATE = 2;

var spam = {
target: '#timeseries',
context: null,
horizon: null,
metrics:null,
format: my_si_format,
click: function(d, i) {
    if ((i > 0) && (i <= 2))
        switch_to_crate(i-1);
    },
state: NEEDS_UPDATE,
slide: 0
};
    
var blah = {
target: '#timeseries-card',
context: null,
horizon: null,
metrics:null,
format: my_si_format,
crate: 0,
click: function(d, i) {
    switch_to_channel(blah.crate, i);
    },
state: NEEDS_UPDATE,
slide: 3
};
    
var channelts = {
target: '#timeseries-channel',
context: null,
horizon: null,
metrics:null,
format: my_si_format,
crate: 0,
card: 0,
state: NEEDS_UPDATE,
slide: 1
};

function setup() {
    SOURCE = $('#data-source').val();
    METHOD = $('#data-method').val();
    STEP = +$('#data-step').val();
    CRATE_WINDOW = +$('#crate-map-window').val();

    var thresholds = default_thresholds[SOURCE];

    SCALE = d3.scale.threshold()
        .domain(thresholds)
        .range(colorbrewer[$("#colors").val()][3]);

    card = card_view()
        .scale(SCALE);

    crate = crate_view()
        .scale(SCALE)
        .click(function(d, i) {
            switch_to_crate(i);
        });

    update_format();
    update_metrics(spam);
    draw(spam);
    spam.state = ACTIVE;

    // set default thresholds in text area
    $('#threshold-lo').val(thresholds[0]);
    $('#threshold-hi').val(thresholds[1]);

}

function update_format() {
    var source = $('#data-source').val();
    var thresholds = default_thresholds[source];

    if (!thresholds) {
        console.error("No thresholds defined for source: " + source);
        return;
    }

    SCALE = d3.scale.threshold()
        .domain(thresholds)
        .range(colorbrewer[$("#colors").val()][3]);

    set_thresholds(thresholds[0], thresholds[1]);
}

var timeseries = [spam, blah, channelts];

setup();

function update_state(call_update_metric) {
    call_update_metric = typeof call_update_metric === 'undefined' ? true : false;

    timeseries.forEach(function(ts) {
        switch (ts.state) {
            case ACTIVE:
                if (call_update_metric)
                    update_metrics(ts);
                draw(ts);
                break;
            case PAUSED:
                if (call_update_metric)
                    ts.state = NEEDS_UPDATE;
                else
                    draw(ts);
        }
    });
}

$('#data-method').change(function() {
    METHOD = this.value;

    update_state();
});

$('#colors').change(function() {
    SCALE.range(colorbrewer[this.value][3]);
    update_format();
    update();
    update_state();
});

$('#crate-map-window').change(function() {
    CRATE_WINDOW = this.value;

    update();
});

$('#data-step').change(function() {
    STEP = this.value;

    update_state();
});

$('#data-source').change(function() {
    // update threshold values
    var thresholds = default_thresholds[this.value];
    set_thresholds.apply(this,thresholds);

    SOURCE = this.value;
    SCALE.domain(thresholds);
    update_format();

    update();

    update_state();
});

$('#threshold-lo').keypress(function(e) {
    if (e.which == 13) {
        SCALE.domain([this.value,SCALE.domain()[1]]);

        update_state(false);

        d3.select("#crate").call(crate);
        d3.select("#card").call(card);
    }
});

$('#threshold-hi').keypress(function(e) {
    if (e.which == 13) {
        SCALE.domain([SCALE.domain()[0],this.value]);

        update_state(false);

        d3.select("#crate").call(crate);
        d3.select("#card").call(card);
    }
});

$('.carousel').on('slid.bs.carousel', function(e) {
    var slide = $(e.relatedTarget).index();
    $('#card-heading').text('Crate ' + blah.crate);
    $('#channel-heading').text('Crate ' + channelts.crate + ', Card ' + channelts.card);
    $('.data-source-heading').text($('#data-source :selected').text());

    timeseries.forEach(function(ts) {
        if (ts.slide == slide) {
            if (ts.state == NEEDS_UPDATE) {
                update_metrics(ts);
                draw(ts);
                ts.state = ACTIVE;
            } else if (ts.state == PAUSED) {
                ts.context.start();
                ts.state = ACTIVE;
            } else {
                console.log('timeseries already active');
            }
        } else {
            if (ts.state == ACTIVE) {
                ts.context.stop();
                ts.state = PAUSED;
            }
        }
    });
});

function query(name){
	console.log("Fetching data");
        console.log("query_name"+name) //Samm
	/* return context.metric(function(name, callback) {
	$.getJSON($SCRIPT_ROOT + '/query', {name: SOURCE, step: CRATE_WINDOW})}); */
};

function add_horizon(expressions, format, colors, extent) {
    var horizon = context.horizon().height(Number(height));

    if (typeof format != "undefined") horizon = horizon.format(format);
    if (typeof colors != "undefined" && colors) horizon = horizon.colors(colors);
    if (typeof extent != "undefined") horizon = horizon.extent(extent);

    d3.select('#main').selectAll('.horizon')
        .data(expressions.map(query), String)
      .enter().insert('div','.bottom')
        .attr('class', 'horizon')
        .call(horizon)
        .on('click', function(d, i) {
            var domain = context.scale.domain();
            var params = {
                name: expressions[i],
                start: domain[0].toISOString(),
                stop: domain[domain.length-1].toISOString(),
                step: Math.floor(context.step()/1000)
            };
            window.open($SCRIPT_ROOT + "/graph?" + $.param(params), '_self');
        });
}

var interval = 5000;

function update() {
    $.getJSON($SCRIPT_ROOT + '/query', {name: SOURCE, step: CRATE_WINDOW})
        .done(function(result) {
            d3.select('#crate').datum(result.values).call(crate);
            d3.select('#card').datum(result.values).call(card);
            d3.select('#timeseries-card').datum(result.values);
            //d3.select("#bargraph").selectAll("svg").remove()

            newData = []

            for (value of result.values){
                if(value==null){
                    console.log("Ignoring value")
                    continue
                }else{
                    console.log("Pushing value" + value)
                    newData.push(value)
                }
            }
           console.log(newData)//samm
           console.log("update_name"+SOURCE) //samm
            d3.select('#bargraph')
            .select("svg")
            .html("");

            d3.select("#bargraph")
            .select("svg")
            .selectAll("rect")
            .data(newData)
            .enter()
            .append("rect")
            .attr("width", function(d){
                if(d==0){
                    return 0;
                }else{
                    return widthScale(d);
                }
            })
            .attr("height",10)
            .attr("y", function(d,i){ return i*10});

            d3.select("#bargraph")
            .select("svg").append("g")
            .attr("transform", "translate(0,480)")
            .call(axis);
        });
	update_state(true);
    console.log("Updated data");
}
var context = create_context('#main', $('#data-step').val());

add_horizon(["base"], format_rate, null, [0,10000]);

d3.select('#crate').datum([]).call(crate);
d3.select('#card').datum([]).call(card);
// wrap first ten and last ten crates in a div
$('#crate' + [0,1,2,3,4,5,6,7,8,9].join(',#crate')).wrapAll('<div />');
$('#crate' + [0,1,2,3,4].join(',#crate')).wrapAll('<div style="display:inline-block" />');
$('#crate' + [5,6,7,8,9].join(',#crate')).wrapAll('<div style="display:inline-block" />');
$('#crate' + [10,11,12,13,14,15,16,17,18,19].join(',#crate')).wrapAll('<div />');
$('#crate' + [10,11,12,13,14].join(',#crate')).wrapAll('<div style="display:inline-block" />');
$('#crate' + [15,16,17,18,19].join(',#crate')).wrapAll('<div style="display:inline-block" />');
update();
setInterval(update,interval);

var dataArray = [10,30,40,50];

var widthScale = d3.scale.linear()
                .domain([500,600])
                .range([0,500]);

var canvas = d3.select("#bargraph")
.append("svg")
.attr("width", 500)
.attr("height",500);

var axis = d3.svg.axis()
.ticks(5)
.scale(widthScale);

canvas.append("g")
.attr("transform", "translate(0,480)")
.call(axis);

// Attach click handler to <td id="channel"> elements
$(document).on('click', 'td#channel', function(e) {
    var title = $(this).attr('title'); // e.g., "Card 7, Channel 15"
    var match = /Card (\d+), Channel (\d+)/.exec(title);
    if (match) {
        var card = parseInt(match[1], 10);
        // Always call switch_to_channel(0, card)
        console.log('Clicked card', card, 'channel 0');
        switch_to_channel(0, card);
    }
});
