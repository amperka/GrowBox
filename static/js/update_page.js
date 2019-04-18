
function callback(data, status) {
	if (status == "success") {
        var gaugeElem = document.getElementsByClassName("canv")[0];
		gaugeElem.setAttribute("data-value", data);

		// var chartCanv = document.getElementById("chartCanv")
		// var time = (new Date()).getSeconds()
		// if (window.chart != undefined) {
		// 	if (chart.data.labels.length < 10) {
		// 		chart.data.labels.push(time);
		// 		chart.data.datasets[0].data.push(data);
		// 	}
		// 	else {
		// 		chart.data.labels.push(time);
		// 		chart.data.labels.shift();
		// 		chart.data.datasets[0].data.push(data);
		// 		chart.data.datasets[0].data.shift();
		// 	}
		// 	window.chart.update();
		// }
		setTimeout(getReading, 1000, url);
	}
	else {
		alert("Problem");
	}
}

function getReading(url){
	$.get(url, callback);
}

