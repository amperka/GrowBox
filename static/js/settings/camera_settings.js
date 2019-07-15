function removeFrames() {
    var removeFrameMsg = {
        msgYes: "Старые кадры успешно удалены",
        msgNo: "Кадры отсутствуют",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер.",
        callback: function(msg) {
            addMsgToDiv(msg);
        },
    };
    request("/remove_frames", removeFrameMsg, false);
}

function removeVideo() {
    var removeVideoMsg = {
        msgYes: "Видеозапись успешно удалена.",
        msgNotFound: "Видеозапись не найдена.",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер.",
        callback: function(msg) {
            addMsgToDiv(msg);
        },
    };
    request("/remove_video", removeVideoMsg, false);
}

function downloadVideo() {
    var downloadVideoMsg = {
        msgYes: "Видео успешно скачано.",
        msgNo: "USB-устройство не обнаружено. Проверьте подключение.",
        msgNotFound: "Видеозапись не найдена. Создайте видеозапись.",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер.",
        callback: function(msg) {
            addMsgToDiv(msg);
        },
    };
    request("/download/video", downloadVideoMsg, true);
}

function extractUsb() {
    var extractMsg = {
        msgYes: "USB-устройство может быть извлечено.",
        msgNo: "USB-устройство не обнаружено. Проверьте подключение.",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер.",
        callback: function(msg) {
            addMsgToDiv(msg);
        },
    };
    request("/extract_usb", extractMsg, false);
}

function addMsgToDiv(msg) {
	var div = document.getElementById("camera-msg");
	div.innerHTML = msg;
	$("#camera-msg").fadeIn();
	setTimeout(function() {
		$("#camera-msg").fadeOut();
	}, 3000);
}

$("#del-img-button").click(function () {
    Confirm("Удалить кадры", "Вы действительно хотите удалить кадры камеры?", "Да", "Нет", removeFrames);
});

$("#del-video-button").click(function () {
    Confirm("Удалить видео", "Вы действительно хотите удалить видеозапись?", "Да", "Нет", removeVideo);
});

$("#load-video-button").click(function () {
    Confirm("Скачать видео", "Вы действительно хотите скачать видеозапись?", "Да", "Нет", downloadVideo);
});

$("#extract").click(function() {
    Confirm("Извлечь накопитель", "Вы действительно хотите извлечь накопитель?", "Да", "Нет", extractUsb);
});

