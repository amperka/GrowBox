function disableRadioButtons(radioButtons) {
    radioButtons.forEach(function (radio) {
        radio.disabled = true;
    });
}

function enableRadiosButtons(radioButtons) {
    radioButtons.forEach(function (radio) {
        radio.disabled = false;
    });
}

function setChanges() {
    var lamp = document.querySelector("#lamp-switch");
    var fan = document.querySelector("#fan-switch");
    var compressor = document.querySelector("#compressor-switch");
    var lampValues = document.getElementsByName("lamp-radio");
    var fanValues = document.getElementsByName("fan-radio");

    var request = {
        lamp: [0, 0],
        fan: [0, 0],
        compressor: 0
    };

    if (lamp.checked) {
        request.lamp[0] = 1;
        enableRadiosButtons(lampValues);
    } else {
        disableRadioButtons(lampValues);
    }

    if (fan.checked) {
        request.fan[0] = 1;
        enableRadiosButtons(fanValues);
    } else {
        disableRadioButtons(fanValues);
    }

    if (compressor.checked) {
        request.compressor = 1;
    }

    if (lampValues[0].checked) {
        request.lamp[1] = 18;
    } else if (lampValues[1].checked) {
        request.lamp[1] = 12;
    }

    fanValues.forEach(function (value, i) {
        if (value.checked) {
            request.fan[1] = parseInt((document.getElementsByClassName("fan-label")[i].textContent.split(' '))[0]);
        }
    });

    console.log("request:", request); // testing

    $.ajax({
        url: "/accept_settings",
        type: "POST",
        data: JSON.stringify(request),
        contentType: "application/json; charset=utf8",
        dataType: "json",
        success: function () {
            console.log("Настройки приняты");
        }
    });
}

function setCurrState(currentState) {
    console.log(currentState); //testing

    var isLampSwitchChecked = !!currentState.lamp[0];
    var isFanSwitchChecked = !!currentState.fan[0];
    var isCompressorSwitchChecked = !!currentState.compressor;

    var lampRadios = document.getElementsByName("lamp-radio");
    switch (currentState.lamp[1]) {
        case 18:
            lampRadios[0].checked = true;
            break;
        case 12:
            lampRadios[1].checked = true;
            break;
        default:
            break;
    }
    var fanRadios = document.getElementsByName("fan-radio");
    switch (currentState.fan[1]) {
        case 1:
            fanRadios[0].checked = true;
            break;
        case 2:
            fanRadios[1].checked = true;
            break;
        case 4:
            fanRadios[2].checked = true;
            break;
        case 8:
            fanRadios[3].checked = true;
            break;
        default:
            break;
    }

    document.getElementById("lamp-switch").checked = isLampSwitchChecked;
    if (isLampSwitchChecked) {
        enableRadiosButtons(lampRadios);
    } else {
        disableRadioButtons(lampRadios);
    }

    document.getElementById("fan-switch").checked = isFanSwitchChecked;
    if (isFanSwitchChecked) {
        enableRadiosButtons(fanRadios);
    } else {
        disableRadioButtons(fanRadios);
    }

    document.getElementById("compressor-switch").checked = isCompressorSwitchChecked;
}
