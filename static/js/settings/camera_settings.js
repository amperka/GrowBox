import Response from "/static/js/tools/response.js";
import getRequest from "/static/js/tools/request.js";

const requestFuncs = (function() {
    const removeFrameResp = new Response({
        msgYes: "Старые кадры успешно удалены",
        msgNo: "Кадры отсутствуют",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер.",
        preloader: false,
    });

    const removeVideoResp = new Response({
        msgYes: "Видеозапись успешно удалена.",
        msgNotFound: "Видеозапись не найдена.",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер.",
        preloader: false,
    });

    const downloadVideoResp = new Response({
        msgYes: "Видео успешно скачано.",
        msgNo: "USB-устройство не обнаружено. Проверьте подключение.",
        msgNotFound: "Видеозапись не найдена. Создайте видеозапись.",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер.",
        preloader: true,
    });

    const extractResp = new Response({
        msgYes: "USB-устройство может быть извлечено.",
        msgNo: "USB-устройство не обнаружено. Проверьте подключение.",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер.",
        preloader: false,
    });

    let arrOfResp = [
        removeFrameResp,
        removeVideoResp,
        downloadVideoResp,
        extractResp
    ];

    arrOfResp.forEach((obj) => {
        if (typeof obj.msgYes !== "undefined") {
            obj.success = function () {
                addMsgToDiv("#camera-msg", this.msgYes);
            };
        }
        if (typeof obj.msgNo !== "undefined") {
            obj.fail = function() {
                addMsgToDiv("#camera-msg", this.msgNo);
            };
        }
        if (typeof obj.msgError !== "undefined") {
            obj.error = function() {
                Alert("Ошибка!", this.msgError);
            };
        }
        if (typeof obj.msgNotFound !== "undefined") {
            obj.notFound = function() {
                addMsgToDiv("#camera-msg", this.msgNotFound);
            };
        }
    });

    return {
        removeFrames: () => getRequest("/remove_frames", removeFrameResp, true),
        removeVideo: () => getRequest("/remove_video", removeVideoResp, true),
        downloadVideo: () => getRequest("/download/video", downloadVideoResp, true),
        extractUsb: () => getRequest("/extract_usb", extractResp, true),
    };
})();

$(function() {
    $("#del-img-button").click(function () {
        Confirm(
            "Удалить кадры",
            "Вы действительно хотите удалить кадры камеры?",
            "Да",
            "Нет",
            requestFuncs.removeFrames
        );
    });

    $("#del-video-button").click(function () {
        Confirm(
            "Удалить видео",
            "Вы действительно хотите удалить видеозапись?",
            "Да",
            "Нет",
            requestFuncs.removeVideo
        );
    });

    $("#load-video-button").click(function () {
        Confirm(
            "Скачать видео",
            "Вы действительно хотите скачать видеозапись?",
            "Да",
            "Нет",
            requestFuncs.downloadVideo
        );
    });

    $("#extract").click(function() {
        Confirm(
            "Извлечь накопитель",
            "Вы действительно хотите извлечь накопитель?",
            "Да",
            "Нет",
            requestFuncs.extractUsb
        );
    });
});

