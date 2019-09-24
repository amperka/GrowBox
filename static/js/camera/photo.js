import Response from "/static/js/tools/response.js";
import getRequest from "/static/js/tools/request.js";

const requestFuncs = (function() {
    const photoResp1 = new Response({
        msgNo: "Камера недоступна. Проверьте подключение камеры.",
        msgError: "Перезагрузите гроукомпьютер.",
    });
    photoResp1.fail = function() {
        Alert("Предупреждение!", this.msgNo);
    };
    photoResp1.error = function() {
        Alert("Ошибка!", this.msgError);
    };
    photoResp1.success = function() {
        createImage("image1");
    };

    const photoResp2 = new Response({
        msgNo: "Камера недоступна. Проверьте подключение камеры.",
        msgError: "Перезагрузите гроукомпьютер.",
    });
    photoResp2.fail = function() {
        Alert("Предупреждение!", this.msgNo);
    };
    photoResp2.error = function() {
        Alert("Ошибка!", this.msgError);
    };
    photoResp2.success = function() {
        createImage("image2");
    };

    const clearPhotoObj = new Response({
        msgError: "При удалении возникла ошибка. Перезагрузите гроукомпьютер.",
    });
    clearPhotoObj.success = function() {
        location.reload(true);
    };
    clearPhotoObj.error = function() {
        Alert("Ошибка!", this.msgError);
    };

    return {
        requestPhoto: (url, id) => {
            if (id === "image1") {
                getRequest(url, photoResp1, false);
            } else if (id === "image2") {
                getRequest(url, photoResp2, false);
            }
        },
        clearPhoto: () => getRequest("/clear_photo", clearPhotoObj, true),
    };
})();

function createImage(id) {
    let img = new Image(480, 320);
    let placeid;
    if (id === "image1") {
        img.src = "/static/img/img1.jpg?" + Math.random();
        placeid = "place1";
        img.onclick = () => {
            requestFuncs.requestPhoto("/make_photo/img1", "image1");
        };
    } else if (id === "image2") {
        img.src = "/static/img/img2.jpg?" + Math.random();
        placeid = "place2";
        img.onclick = () => {
            requestFuncs.requestPhoto("/make_photo/img2", "image2");
        };
    }
    img.style["border"] ="3px double black";
    img.onload = () => {
        let elemById = document.getElementById(placeid);
        elemById.removeChild(document.getElementById(id));
        elemById.appendChild(img);
        elemById.children[0].setAttribute("id", id);
    };
}

$(function() {
    $("#clear-button").click(function () {
        Confirm(
            "Удалить снимки",
            "Вы действительно хотите удалить снимки?",
            "Да",
            "Нет",
            requestFuncs.clearPhoto
        );
    });

    $("#image1").click(function () {
        requestFuncs.requestPhoto("/make_photo/img1", "image1");
    });

    $("#image2").click(function () {
        requestFuncs.requestPhoto("/make_photo/img2", "image2");
    });
});
