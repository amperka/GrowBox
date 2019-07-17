function updateSystem() {
    var updateMsg = {
        msgYes: "Обновление системы завершено. Чтобы завершить обновление, требуется перезагрузка.",
        msgNo: "Ошибка при обновлении. Проверьте подключение к сети.",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер.",
        callback: function(msg) {
            Alert("Обновление системы", msg);
        },
    };
    request("/update_system", updateMsg, true);
}

function connectToNet() {
    var login = $("input[name=login]").val();
    var passwd = $("input[name=passwd]").val();
    if ((login === "") || (passwd === "")) {
        Alert("Подключение к сети", "Введите имя сети и пароль");
        return;
    }
    $("#preloader").fadeIn();
        $.ajax({
            url:  "/apply_net_settings",
            type: "POST",
            data: JSON.stringify({"login": login, "passwd": passwd,}),
            contentType: "application/json; charset=utf8",
            dataType: "json",
        })
        .done(function () {
            Alert("Подключение к сети", "Подключение к сети " + login + " завершено");
            $("#preloader").fadeOut();
        })
        .fail(function () {
            Alert("Подключение к сети", "Не удалось подключиться к сети " + login);
            $("#preloader").fadeOut();
        });
}

$('#update-button').click(function () {
	Confirm('Обновить систему', 'Вы действительно хотите обновить систему?', 'Да', 'Нет', updateSystem);
});

$("#netName").click(function() {
    keyboardModule.openKeyboard();
});

$("#netPassword").click(function() {
    keyboardModule.openKeyboard();
});

