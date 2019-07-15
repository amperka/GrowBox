function calibrate(url, msg) {
    $("#preloader").fadeIn();
    setTimeout(function() {
        $.get(url, function(data) {
            console.log(data);
            respStatus = JSON.parse(data);
            if (respStatus["success"] == true) {
                Alert("Калибровка завершена", "Калибровка " + msg + " успешно завершена");
            } else {
                Alert("Ошибка калибровки!", "Ошибка калибровки " + msg + "! Пожалуйста, повторите.");
            }
            })
            .fail(function() {
                Alert("Ошибка калибровки!", "Ошибка калибровки " + msg + "! Пожалуйста, повторите.");}
            );
        $("#preloader").fadeOut();
    }, 5000);
}

$("#calibrateFour").click(function() {
    calibrate("/calibration/four", "4.01");
});

$("#calibrateSeven").click(function() {
    calibrate("/calibration/seven", "7.01");
});

