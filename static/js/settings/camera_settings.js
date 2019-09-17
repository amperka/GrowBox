function removeFrames() {
    let removeFrameMsg = {
        msgYes: "Старые кадры успешно удалены",
        msgNo: "Кадры отсутствуют",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер.",
        callback: function(msg) {
            addMsgToDiv("#camera-msg",msg);
        },
    };
    request("/remove_frames", removeFrameMsg, false);
}

function removeVideo() {
    let removeVideoMsg = {
        msgYes: "Видеозапись успешно удалена.",
        msgNotFound: "Видеозапись не найдена.",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер.",
        callback: function(msg) {
            addMsgToDiv("#camera-msg", msg);
        },
    };
    request("/remove_video", removeVideoMsg, false);
}

function downloadVideo() {
    let downloadVideoMsg = {
        msgYes: "Видео успешно скачано.",
        msgNo: "USB-устройство не обнаружено. Проверьте подключение.",
        msgNotFound: "Видеозапись не найдена. Создайте видеозапись.",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер.",
        callback: function(msg) {
            addMsgToDiv("#camera-msg", msg);
        },
    };
    request("/download/video", downloadVideoMsg, true);
}

function extractUsb() {
    let extractMsg = {
        msgYes: "USB-устройство может быть извлечено.",
        msgNo: "USB-устройство не обнаружено. Проверьте подключение.",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер.",
        callback: function(msg) {
            addMsgToDiv("#camera-msg", msg);
        },
    };
    request("/extract_usb", extractMsg, false);
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

