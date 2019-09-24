import Response from "/static/js/tools/response.js";
import getRequest from "/static/js/tools/request.js";

const requestFuncs = (function() {
    const startRecResp = new Response({
        msgNo: "Камера недоступна. Проверьте подключение камеры!",
        msgError: "Перезагрузите гроукомпьютер.",
        preloader: false,
    });
    startRecResp.success = function() {
        $("#recButton").removeClass("notRec");
        $("#recButton").addClass("Rec");
        $("#recMess").html("Остановить запись");
    };
    startRecResp.fail = function() {
        Alert("Предупреждение!", this.msgNo);
    };
    startRecResp.error = function() {
        Alert("Ошибка!", this.msgError);
    };

    const finishRecResp = new Response({
        msgError: "Перезагрузите гроукомпьютер.",
        msgNo: "Запись не ведется. Включите запись.",
        preloader: false,
    });
    finishRecResp.success = function() {
        $("#recButton").removeClass("Rec");
        $("#recButton").addClass("notRec");
        $("#recMess").html("Включить запись");
    };
    finishRecResp.fail = function() {
        Alert("Предупреждение!", this.msgNo);
    };
    finishRecResp.error = function() {
        Alert("Ошибка!", this.msgError);
    };

    const makeVideoResp = new Response({
        msgNo: "Отсутствуют кадры для создания видео.",
        msgError: "Перезагрузите гроукомпьютер.",
        preloader: true,
    });
    makeVideoResp.success = function() {
        watchVideo();
    };
    makeVideoResp.fail = function() {
        Alert("Предупреждение!", this.msgNo);
    };
    makeVideoResp.error = function() {
        Alert("Ошибка!", this.msgError);
    };

    return {
        startRecord: () => getRequest("/start_record", startRecResp, false),
        finishRecord: () => getRequest("/finish_record", finishRecResp, false),
        makeVideo: () => getRequest("/make_video", makeVideoResp, true),
    };
})();


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

$(function(){
    $('#recButton').click(function(){
	    if($('#recButton').hasClass('notRec')){
		    requestFuncs.startRecord();
    	} else {
		    requestFuncs.finishRecord();
	    }
    });

    $('#make-button').click(function() {
        requestFuncs.makeVideo();
    });
});
