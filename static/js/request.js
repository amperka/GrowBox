function request(url, obj, preloader) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.send();
    if (preloader) {
        $("#preloader").fadeIn();
    }
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return;
        if (preloader) {
            $("#preloader").fadeOut();
        }
        switch(xhr.status) {
            case 200:
                obj.callback(obj.msgYes);
                break;
            case 403:
                obj.callback(obj.msgNo);
                break;
            case 404:
                obj.callback(obj.msgNotFound);
                break;
            case 500:
                obj.callback(obj.msgError);
                break;
            default:
                obj.callback(obj.msgError);
        }
    }
}

