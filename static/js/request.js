function request(url, obj, preloader) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.send();
    if (preloader) {
        $("#preloader").fadeIn();
    }
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return;
        if (xhr.status == 200) {
            if (preloader){
                $("#preloader").fadeOut();
            }
            obj.callback(obj.msgYes);
        } else if (xhr.status == 403) {
            if (preloader) {
                $("#preloader").fadeOut();
            }
            obj.callback(obj.msgNo);
        } else {
            obj.callback(obj.msgError);
        }
    }
}

