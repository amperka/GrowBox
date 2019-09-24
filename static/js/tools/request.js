export default function getRequest(url, obj, async=true) {
    let xhr = new XMLHttpRequest();
    xhr.open("GET", url, async);
    xhr.send();
    if (obj.preloader) {
        $("#preloader").fadeIn();
    }
    if (!async) {
        obj.callback(xhr.status);
        return;
    }
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return;
        if (obj.preloader) {
            $("#preloader").fadeOut("slow", function() {
                obj.callback(xhr.status);
            });
        } else {
            obj.callback(xhr.status);
        }
    }
}
