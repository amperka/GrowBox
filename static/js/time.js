window.onload = function(){
	(function curr_time(){
		var date = new Date();
		document.getElementById("clock").innerHTML = date.toLocaleTimeString();
		window.setTimeout(curr_time, 1000);
	})();
};
						
