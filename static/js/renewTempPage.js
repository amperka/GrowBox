
function callback(tempHumStr, status) {
	if (status == "success") {
		var parseStr = tempHumStr.split(' ');
		var temp = parseStr[0];
		var hum = parseStr[1];
		var gaugeTempElem = document.getElementById("tempcanv");
		gaugeTempElem.setAttribute("data-value", temp);
		var gaugeHumElem = document.getElementById("humcanv");
		gaugeHumElem.setAttribute("data-value", hum);
		setTimeout(getReading, 1000);
	}
	else {
		alert("Problem");
	}
}

function getReading(){
	$.get('/tempmeas', callback);
}
