import Response from "/static/js/tools/response.js";
import getRequest from "/static/js/tools/request.js";

const requestFuncs = (function() {
    const updateResp = new Response({
        msgYes: "Обновление системы завершено. Чтобы завершить обновление, требуется перезагрузка.",
        msgNo: "Ошибка при обновлении. Проверьте подключение к сети.",
        msgError: "Возникла ошибка системы. Перезагрузите гроукомпьютер.",
        preloader: true,
    });
    updateResp.success = function() {
        Alert("Обновление системы.", this.msgYes);
    };
    updateResp.fail = function() {
        Alert("Обновление системы.", this.msgNo);
    };
    updateResp.error = function() {
        Alert("Ошибка!", this.msgError);
    };

    const updateSystem = () => getRequest("/update_system", updateResp, true);
    const connectToNet = () => {
        let login = $("input[name=login]").val();
        let passwd = $("input[name=passwd]").val();
        if ((login === "") || (passwd === "")) {
            Alert("Подключение к сети.", "Введите имя сети и пароль.");
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
            $("#preloader").fadeOut("slow", function(){
                Alert("Подключение к сети.", "Подключение к сети " + login + " завершено.");
            });
        })
        .fail(function () {
            $("#preloader").fadeOut("slow", function() {
                Alert("Подключение к сети.", "Не удалось подключиться к сети " + login + ". Проверьте имя сети и пароль.");
            });
        });
    };
    return {
        updateSystem,
        connectToNet,
    };
})();

$(function() {
    $('#update-button').click(function() {
        Confirm(
            "Обновить систему",
            "Вы действительно хотите обновить систему?",
            "Да",
            "Нет",
            requestFuncs.updateSystem
        );
    });

    $("#connect-button").click(function () {
        requestFuncs.connectToNet();
    });

    $("#netName").click(function() {
        keyboardModule.openKeyboard();
    });

    $("#netPassword").click(function() {
        keyboardModule.openKeyboard();
    });
});
