function startRecord() {
	var xhr = new XMLHttpRequest();
	xhr.open("GET", "/start_record", true);
	xhr.send();
	xhr.onreadystatechange = function() {
		if (xhr.readyState != 4) return;
		if (xhr.status == 200) {
			$("#recButton").removeClass("notRec");
            $("#recButton").addClass("Rec");
            $("#recMess").html("Остановить запись");
		} else if (xhr.status == 403) {
			Alert("Предупреждение!","Камера недоступна. Проверьте подключение камеры!");
		} else {
			alert(xhr.status + ': ' + xhr.statusText);
		}
	}
}

function finishRecord() {
	var xhr = new XMLHttpRequest();
	xhr.open("GET", "/finish_record", true);
	xhr.send();
	xhr.onreadystatechange = function() {
		if (xhr.readyState != 4) return;
		if (xhr.status == 200) {
			$("#recButton").removeClass("Rec");
            $("#recButton").addClass("notRec");
            $("#recMess").html("Включить запись");
		} else if (xhr.status == 403) {
				//addMsgToDiv("Запись не ведётся. Включите запись!");
		} else {
			alert(xhr.status + ': ' + xhr.statusText);
		}
	}
}

function makeVideo() {
	var xhr = new XMLHttpRequest();
	xhr.open('GET', '/make_video', true);
	xhr.send();
	$("#preloader").fadeIn();
	xhr.onreadystatechange = function() {
		if (xhr.readyState != 4) return;
		if (xhr.status == 200) {
			watchVideo();
			$("#preloader").fadeOut();
		} else if (xhr.status == 403) {
            $("#preloader").fadeOut('slow', function() {
                Alert("Ошибка!", "Отсутствуют кадры для видео");
            });
		} else {
			alert(xhr.status + ': ' + xhr.statusText);
		}
	}
}

function watchVideo() {
    $('#image-place').empty();
	var video = document.createElement("video");
    var videoPath = "/static/img/timelapse.mp4?" + Math.random();
	video.setAttribute("src", videoPath);
	video.setAttribute("width", "480");
    video.setAttribute("height", "320");
    video.controls = true;
    video.disablePictureInPicture = true;
    video.setAttribute("controlsList", "nodownload noremoteplayback");
	document.getElementById("image-place").appendChild(video);
}

