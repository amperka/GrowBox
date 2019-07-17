function downloadLogs() {
    let downloadMsg = {
        msgYes: "Журнал успешно скачан.",
        msgNo: "USB-устройство не обнаружено. Проверьте подключение.",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер",
        callback: function(msg) {
            addMsgToDiv(msg);
        },
    };
    request("/download/log", downloadMsg, true);
}

function extractUsb() {
    let extractMsg = {
        msgYes: "USB-устройство может быть извлечено.",
        msgNo: "USB-устройство не обнаружено. Проверьте подключение.",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер",
        callback: function(msg) {
            addMsgToDiv(msg);
        },
    };
    request("/extract_usb", extractMsg, false);
}

function addMsgToDiv(msg) {
	let div = document.getElementById("msg-box");
	div.innerHTML = msg;
	$("#msg-box").fadeIn();
	setTimeout(function() {
		$("#msg-box").fadeOut();
	}, 4000);
}

$("#download-button").click(function() {
    Confirm("Скачать журнал", "Вы действительно хотите скачать журнал?", "Да", "Нет", downloadLogs);
});

$("#extract").click(function() {
    Confirm("Извлечь накопитель", "Вы действительно хотите извлечь накопитель?", "Да", "Нет", extractUsb);
});

