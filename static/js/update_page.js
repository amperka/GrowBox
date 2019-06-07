
function callback(data, status) {
	if (status == "success") {
        var gaugeElem = document.getElementsByClassName("canv")[0];
		gaugeElem.setAttribute("data-value", data);
        setTimeout(getReading, 1000, url);
	}
	else {
		alert("Problem");
	}
}

function getReading(url){
	$.get(url, callback);
}

