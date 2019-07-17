function sendPasswd() {
    var passwd = document.getElementsByName("passwd")[0].value;
    $.ajax({
        url: "/teacher_settings",
        type: "POST",
        data: JSON.stringify({"passwd" : passwd}),
            contentType: "application/json; charset=utf8",
            dataType: "json",
    })
    .fail(function() {
        $("#wrong-passwd").fadeIn();
        setTimeout(function() {
            $("#wrong-passwd").fadeOut();
        }, 3000);
    })
    .done(function() {
        window.location.href="/teacher_page";
    });
}

$("#password").click(function () {
    openKeyboard();
});

createNumKeyboard("#password", "dark");
