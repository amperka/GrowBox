function reboot() {
    $.get("/reboot", function() {
        console.log("Перезагрузка");
        })
        .fail(function() {
            console.log("Ошибка перезагрузки");
        });
}

$("#reboot-btn").click(function() {
    Confirm("Перезагрузить гроукомпьютер", "Вы действительно хотите перезагрузить гроукомпьютер?", "Да", "Нет", reboot);
});

