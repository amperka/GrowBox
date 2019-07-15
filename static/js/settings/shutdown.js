function reboot() {
    $.get("/reboot", function () {
        console.log("Перезагрузка");
        })
        .fail(function () {
            console.log("Ошибка перезагрузки");
        });
}

function shutdown() {
    $.get("/shutdown/shutdown", function () {
        console.log("Выключение");
    })
    .fail(function () {
        console.log("Ошибка выключения");
    });
}

$("#reboot-btn").click(function () {
    Confirm("Перезагрузить гроукомпьютер", "Вы действительно хотите перезагрузить гроукомпьютер?", "Да", "Нет", reboot);
});

$("#shutdown-btn").click(function () {
    Confirm("Выключение гроукомпьютера", "Вы действительно хотите выключить гроукомпьютер?", "Да", "Нет", shutdown);
});
