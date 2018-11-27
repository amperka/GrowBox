window.onload = function() {
	function formatDisplayTime(time) {
		var hours = time.getHours();
		var minutes = time.getMinutes();
		var seconds = time.getSeconds();

		if (hours < 10) {
			hours = '0' + hours;
		}

		if (minutes < 10) {
			minutes = '0' + minutes;
		}

		if (seconds < 10) {
			seconds = '0' + seconds;
		}

		return [hours, minutes, seconds].join(':');
    }

    function tickTimer() {
		document.getElementById("clock").innerHTML = formatDisplayTime(new Date());
    }

	window.setInterval(tickTimer, 1000);
};
						
