function request_photo(url, id) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.send();
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return;

        if (xhr.status == 200) {
            var img = new Image(480, 320);
            var placeid;
            if (id == 'image1') {
                img.src = "/static/img/img1.jpg?" + Math.random();
                placeid = "place1";
                img.onclick = function() {request_photo('/make_photo/img1', 'image1')};
            } else if (id == 'image2') {
                img.src = "/static/img/img2.jpg?" + Math.random();
                placeid = "place2";
                img.onclick = function() {request_photo('/make_photo/img2', 'image2')};
            }
            img.style["border"] ="3px double black";
            img.onload = function () {
                document.getElementById(placeid).removeChild(document.getElementById(id));
                document.getElementById(placeid).appendChild(img);
                document.getElementById(placeid).children[0].setAttribute("id", id);
            }
        } else if (xhr.status == 403) {
            Alert("Предупреждение!", "Камера недоступна. Проверьте подключение камеры.");
        } else {
            Alert("Ошибка!", "Перезагрузите компьютер.");
        }
    }
}

function clearPhoto() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/clear_photo', true);
    xhr.send();
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return;

        if (xhr.status != 200) {
            Alert("Ошибка!", "При удаление возникли проблемы. Перезагрузите компьютер.");
        } else {
            location.reload(true);
        }
    }
}

$('#clear-button').click(function () {
    Confirm('Удалить снимки', 'Вы действительно хотите удалить снимки?', 'Да', 'Нет', clearPhoto);
});

$("#image1").click(function () {
    request_photo("/make_photo/img1", "image1");
});

$("#image2").click(function () {
    request_photo("/make_photo/img2", "image2");
});
