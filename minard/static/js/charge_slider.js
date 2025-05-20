$(function() {
	$("#chargeSlider").slider({
		range: true,
		min: 0,
		max: 1000,
		values: [0,1000],
		slide: function(event,ui) {
			updateChargeLabels(ui.values[0], ui.values[1]);
		        updateSliderGradient(ui.values[0], ui.values[1]);
                }
	});
	updateChargeLabels(0,1000);
        updateSliderGradient(0,1000);
});

function updateChargeLabels(lower, upper) {
    $("#lowerCharge").text(lower);
    $("#upperCharge").text(upper);
}

function updateSliderGradient(lower, upper) {
    let max=1000;
    let gradient = `linear-gradient(to right,
        blue 0%,
        blue ${lower/max*100}%,
        cyan ${lower/max*100}%, 
        green ${(lower+(upper-lower)/4)/max*100}%,
        yellow ${(lower+3*(upper-lower)/4)/max*100}%,
        red ${upper/max*100}%,
        red 100%)`;
    $("#chargeSlider .ui-slider").css("background", gradient);
    $("#chargeSlider").css("background", gradient);
}
