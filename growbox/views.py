#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Standard library imports
import os
import subprocess
import shutil
import random
import json
import time
import logging
import signal
from datetime import datetime

# Third party imports
from flask import render_template, make_response, request, Markup, Blueprint
import requests
from requests.exceptions import HTTPError
from crontab import CronTab

# Local application imports
from growbox import usb_camera, systime_settings
from growbox.arduino_thread import input_queue, ARRAY_LEN, lock, sensors_dict
from growbox.database import get_db

main = Blueprint("main", __name__)

views_logger = logging.getLogger(__name__)


# Return index page
@main.route("/")
@main.route("/index")
def index():
    return render_template("index.html", title="Главное меню", lock="/lock")


# Return measurements page
@main.route("/measurements")
def measurements():
    template_data = {"title": "Измерения", "goback": "/index"}
    return render_template("measurements/measurements.html", **template_data)


# Return a specific sensor measurement
@main.route("/measurements/<param>")
def spec_measurements(param):
    if param == "temp":
        title = "Температура"
        label = title
    elif param == "ph":
        title = "Уровень pH"
        label = title
    elif param == "tds":
        title = "Солёность"
        label = "Уровень солей"
    elif param == "co2":
        title = "Углекислый газ"
        label = "CO2"
    template_data = {"title": title, "goback": "/measurements", "label": label}
    return render_template("measurements/" + param + ".html", **template_data)


# Return dynamic measurements
@main.route("/temp_measure")
def temp_meas():
    with lock:
        ret_val = str(sensors_dict["temp"])
    return ret_val


@main.route("/ph_measure")
def ph_meas():
    with lock:
        ret_val = str(sensors_dict["ph"])
    return ret_val


@main.route("/tds_measure")
def tds_meas():
    with lock:
        ret_val = str(sensors_dict["tds"])
    return ret_val


@main.route("/co2_measure")
def co2_meas():
    with lock:
        ret_val = str(sensors_dict["co2"])
    return ret_val


# Camera control
@main.route("/camera")
def camera():
    template_data = {"title": "Камера", "goback": "/index"}
    return render_template("camera/camera.html", **template_data)


@main.route("/camera/photo")
def photo():
    img1_exist = os.path.isfile("./static/img/img1.jpg")
    img2_exist = os.path.isfile("./static/img/img2.jpg")
    img1_name = "img1.jpg?" + str(random.random())
    img2_name = "img2.jpg?" + str(random.random())
    if img1_exist and img2_exist:
        template_data = {
            "img1": img1_name,
            "img2": img2_name,
            "pad1": "0px",
            "pad2": "0px",
        }
    elif img1_exist and not img2_exist:
        template_data = {
            "img1": img1_name,
            "img2": "Camera.png",
            "pad1": "0px",
            "pad2": "50px 120px",
        }
    elif not img1_exist and img2_exist:
        template_data = {
            "img1": "Camera.png",
            "img2": img2_name,
            "pad1": "50px 120px",
            "pad2": "0px",
        }
    else:
        template_data = {
            "img1": "Camera.png",
            "img2": "Camera.png",
            "pad1": "50px 120px",
            "pad2": "50px 120px",
        }
    template_data.update({"title": "Фото", "goback": "/camera"})
    return render_template("camera/photo.html", **template_data)


@main.route("/make_photo/<img>")
def make_photo(img):
    camera = usb_camera.PiCamera(0)
    if img == "img1":
        name = "img1.jpg"
    elif img == "img2":
        name = "img2.jpg"
    try:
        camera.capture("./static/img/" + name, resize=(480, 320))
    except RuntimeError:
        views_logger.error("Photo is not created")
        return make_response("", 403)
    else:
        return make_response("", 200)
    finally:
        views_logger.debug("Camera close")
        camera.close()


@main.route("/clear_photo")
def clear_photo():
    command = "rm -f ./static/img/img*"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as err:
        views_logger.error("clear_photo: Delete error", err)
        return make_response("", 500)
    else:
        views_logger.info("clear_photo: Frames successfully deleted")
        return make_response("", 200)


@main.route("/camera/video")
def video():
    record_status = check_videorecord()
    if record_status:
        record_message = "Остановить запись"
    else:
        record_message = "Включить запись"
    video_exist = os.path.isfile("./static/img/timelapse.mp4")
    video_path = "/static/img/timelapse.mp4?" + str(random.random())
    template_data = {
        "title": "Видео",
        "goback": "/camera",
        "recStatus": record_status,
        "recMess": record_message,
        "videoExist": video_exist,
        "videoPath": video_path,
    }
    return render_template("camera/video.html", **template_data)


@main.route("/start_record")
def start_record():
    try:
        camera = usb_camera.PiCamera(0)
        if not camera.check_connection():
            raise RuntimeError
    except RuntimeError:
        views_logger.error("Camera is not connected")
        return make_response("", 403)
    finally:
        camera.close()
    my_cron = CronTab(user="pi")
    for job in my_cron:
        if job.comment == "Growbox":
            return make_response("", 500)
    curr_dir = os.getcwd()
    command = curr_dir + "/growbox/usb_camera.py"
    job = my_cron.new(command=command, comment="Growbox")
    job.every(1).hours()
    my_cron.write()
    return make_response("", 200)


@main.route("/finish_record")
def finish_record():
    my_cron = CronTab(user="pi")
    for job in my_cron:
        if job.comment == "Growbox":
            my_cron.remove(job)
            my_cron.write()
            return make_response("", 200)
    return make_response("", 403)


@main.route("/remove_frames")
def remove_frames():
    if len(os.listdir("/home/pi/Pictures")) == 0:
        views_logger.debug("Pictures directory is empty")
        return make_response("", 403)
    try:
        command = "rm -f /home/pi/Pictures/*"
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as err:
        views_logger.error("remove_frames: Delete error", err)
        return make_response("", 500)
    else:
        views_logger.info("remove_frames: Frames successfully deleted")
        return make_response("", 200)


@main.route("/remove_video")
def remove_video():
    if os.path.exists("./static/img/timelapse.mp4"):
        try:
            command = ["rm", "-f", "./static/img/timelapse.mp4"]
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as err:
            views_logger.error("remove_video: Delete error", err)
            return make_response("", 500)
        else:
            views_logger.info("remove_video: Video successfully deleted")
            return make_response("", 200)
    views_logger.warning("remove_video: Video not exist, nothing to delete")
    return make_response("", 404)


@main.route("/make_video")
def make_video():
    if len(os.listdir("/home/pi/Pictures")) != 0:
        command = [
            "ffmpeg",
            "-y",
            "-r",
            "10",
            "-i",
            "/home/pi/Pictures/%*.jpg",
            "-r",
            "10",
            "-vcodec",
            "libx264",
            "-vf",
            "scale=480:320",
            "./static/img/timelapse.mp4",
        ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as err:
            views_logger.error("make_video: Video creating error", err)
            return make_response("", 500)
        else:
            views_logger.info("make_video: Video is created")
            return make_response("", 200)
    return make_response("", 403)


# GrowBox settings
@main.route("/settings")
def settings():
    row = get_db().select_activity()
    data = Markup(row[0][0])
    return render_template(
        "/settings/settings.html",
        json_str=data,
        title="Управление",
        goback="/index",
    )


@main.route("/accept_settings", methods=["POST"])
def accept_setting():
    content = request.json
    input_queue.put(str(content))
    get_db().update_activity(str(content))
    return (
        json.dumps({"success": True}),
        200,
        {"ContentType": "application/json"},
    )


# Teacher settings
@main.route("/login")
def secret_page():
    template_data = {"title": "Регистрация", "goback": "/index"}
    return render_template("/settings/login.html", **template_data)


@main.route("/lock")
def lock_page():
    return render_template("/lock.html")


@main.route("/teacher_settings", methods=["POST"])
def log_in():
    content = request.json
    passwd = content["passwd"]
    if passwd == "2486":
        return (
            json.dumps({"success": True}),
            200,
            {"ContentType": "application/json"},
        )
    return make_response("", 403)


@main.route("/teacher_page")
def teacher_page():
    template_data = {"title": "Настройки", "goback": "/index"}
    return render_template("/settings/teacher_settings.html", **template_data)


@main.route("/teacher_page/<settings>")
def teacher_settings(settings):
    ret_val = "/settings/" + settings + ".html"
    if settings == "time_settings":
        title = "Время и дата"
    elif settings == "net_settings":
        title = "Сеть и обновления"
    elif settings == "calibration_page":
        title = "Калибровка датчика pH"
    elif settings == "camera_settings":
        title = "Настройки камеры"
    elif settings == "work_log":
        title = "Журнал работы"
    elif settings == "shutdown_page":
        title = "Завершение работы"
    template_data = {"title": title, "goback": "/teacher_page"}
    return render_template(ret_val, **template_data)


@main.route("/apply_net_settings", methods=["POST"])
def apply_net_settings():
    content = request.json
    login = content["login"]
    passwd = content["passwd"]

    settings_str = (
        "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n"
        + "update_config=1\n"
        + "country=RU\n"
    )
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as file:
        file.write(settings_str)
        file.write(
            '\nnetwork={\n\tssid="'
            + login
            + '"\n\tpsk="'
            + passwd
            + '"\n\tkey_mgmt=WPA-PSK\n}\n'
        )

    os.system("wpa_cli -i wlan0 reconfigure")
    time.sleep(10)
    if is_connected():
        return (
            json.dumps({"success": True}),
            200,
            {"ContentType": "application/json"},
        )
    else:
        return (
            json.dumps({"success": False}),
            403,
            {"ContentType": "application/json"},
        )


@main.route("/update_system")
def update_system():
    if not is_connected():
        return make_response("", 403)
    ret = os.system("echo Update")  # Testing
    time.sleep(5)  # Testing
    # ret = os.system("git pull origin master") # Uncomment to update
    if ret == 0:
        views_logger.info("System update")
        return make_response("", 200)
    else:
        return make_response("", 500)


@main.route("/apply_time", methods=["POST"])
def apply_time():
    content = request.json
    date = content["set-date"]
    time = content["set-time"]

    # Reverse string from %dd-%mm-%yyyy to %yyyy-%mm-%dd
    date = "-".join(date.split("-")[::-1])
    datetime_set = date + " " + time
    try:
        systime_settings.set_systime(datetime_set)
    except subprocess.CalledProcessError:
        views_logger.error("Error setting the system time")
        return (
            json.dumps({"success": False}),
            500,
            {"ContentType": "application/json"},
        )

    datetime_obj = datetime.strptime(datetime_set, "%Y-%m-%d %H:%M")
    fmt_datetime = {"setTime": datetime_obj.strftime("%a %b %d %H:%M:%S %Y")}
    input_queue.put(json.dumps(fmt_datetime))

    return (
        json.dumps({"success": True}),
        200,
        {"ContentType": "application/json"},
    )


@main.route("/calibration/<param>")
def calibration(param):
    if param == "four":
        command = json.dumps({"calibrate": 4})
        input_queue.put(command)
    if param == "seven":
        command = json.dumps({"calibrate": 7})
        input_queue.put(command)
    return (
        json.dumps({"success": True}),
        200,
        {"ContentType": "application/json"},
    )


@main.route("/download/<param>")
def download(param):
    media_dir = os.listdir("/media/pi")
    if len(media_dir) == 0:
        views_logger.error("download/" + param + ": USB-device not found")
        return make_response("", 403)
    usb_path = "/media/pi/" + media_dir[0]
    if param == "log":
        try:
            shutil.copy("./growbox.log", usb_path)
        except Exception as err:
            views_logger.error("download/" + param + ": Copy error")
            views_logger.error(err)
            return make_response("", 500)
        return make_response("", 200)
    elif param == "video":
        if os.path.exists("./static/img/timelapse.mp4"):
            try:
                shutil.copy("./static/img/timelapse.mp4", usb_path)
            except Exception as err:
                views_logger.error("download/" + param + ": Copy error")
                views_logger.error(err)
                return make_response("", 500)
            return make_response("", 200)
        else:
            views_logger.error("download/" + param + ": Video not exist")
            return make_response("", 404)


@main.route("/extract_usb")
def extract_usb():
    media_dir = os.listdir("/media/pi")
    if len(media_dir) == 0:
        views_logger.error("extract_usb: USB-device not found")
        return make_response("", 403)
    command = ["sudo", "umount", "/dev/sda1"]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as err:
        views_logger.error("extract_usb: umount error", err)
        return make_response("", 500)
    return make_response("", 200)


@main.route("/shutdown/<param>")
def shutdown(param):
    os.kill(os.getpid(), signal.SIGTERM)
    shutdown_server = request.environ.get("werkzeug.server.shutdown")
    if shutdown_server is None:
        views_logger.error("Shutdown server is not available")
        return make_response("", 500)
    else:
        shutdown_server()
        if param == "reboot":
            views_logger.debug("System reboot")
            os.system("sleep 10 && sudo reboot &")
            return make_response("", 200)
        elif param == "shutdown":
            views_logger.debug("System shutdown")
            os.system("sleep 10 && sudo shutdown -h now &")
            return make_response("", 200)


# Charts pages
@main.route("/charts")
def charts():
    template_data = {"title": "Журнал", "goback": "/index"}
    return render_template("charts/charts.html", **template_data)


@main.route("/charts/<param>")
def chart_page(param):
    if param == "temp":
        template_data = {"label": "Температура", "title": "Журнал температуры"}
    if param == "acidity":
        template_data = {"label": "Уровень pH", "title": "Журнал уровня pH"}
    if param == "saline":
        template_data = {
            "label": "Уровень солей",
            "title": "Журнал уровня солей",
        }
    if param == "carbon":
        template_data = {
            "label": "Уровень CO2",
            "title": "Журнал концентрации углекислого газа",
        }
    template_data.update({"param": param, "goback": "/charts"})
    return render_template("charts/month_chart.html", **template_data)


@main.route("/charts/draw_chart", methods=["POST"])
def draw_chart():
    if request.json:
        param = request.json["param"]
        period = request.json["period"]
        if period:
            if period == "hour":
                error, data, labels = hour_data(param=[param])
            if period == "day":
                error, data, labels = day_data(param=[param])
            if period == "week":
                error, data, labels = week_data(param=[param])
            if period == "month":
                error, data, labels = month_data(param=[param])

            template_data = {
                "error": error,
                "labels": labels,
                "data": data,
                "param": param,
            }
            return (
                json.dumps(template_data),
                200,
                {"ContentType": "application/json"},
            )


# About plants
@main.route("/info")
def info():
    template_data = {"title": "Справка", "goback": "/index"}
    return render_template("/info/info.html", **template_data)


@main.route("/info/<plant>")
def select_plant(plant):
    ret_val = "/info/" + plant + ".html"
    if plant == "salad":
        title = "Салат"
    elif plant == "bean":
        title = "Фасоль"
    elif plant == "oats":
        title = "Oвёс"
    elif plant == "basil":
        title = "Базилик"
    template_data = {"title": title, "goback": "/info"}
    return render_template(ret_val, **template_data)


def month_data(param):
    now = int(datetime.timestamp(datetime.now()))
    prev_month = now - 2592000
    error, data, labels = prepare_data(
        param, prev_month, now, 2592000 // ARRAY_LEN
    )
    labels = [datetime.fromtimestamp(x).strftime("%d.%m") for x in labels]
    return error, data, labels


def week_data(param):
    now = int(datetime.timestamp(datetime.now()))
    prev_week = now - 604800
    error, data, labels = prepare_data(
        param, prev_week, now, 604800 // ARRAY_LEN
    )
    labels = [datetime.fromtimestamp(x).strftime("%d.%m %Hh") for x in labels]
    return error, data, labels


def day_data(param):
    now = int(datetime.timestamp(datetime.now()))
    prev_day = now - 86400
    error, data, labels = prepare_data(
        param, prev_day, now, 86400 // ARRAY_LEN
    )
    labels = [datetime.fromtimestamp(x).strftime("%H:%M") for x in labels]
    return error, data, labels


def hour_data(param):
    now = int(datetime.timestamp(datetime.now()))
    prev_hour = now - 3600
    error, data, labels = prepare_data(
        param, prev_hour, now, 3600 // ARRAY_LEN
    )
    labels = [datetime.fromtimestamp(x).strftime("%H:%M") for x in labels]
    return error, data, labels


def prepare_data(param, from_time, to_time, limit):
    data = get_db().select_sensors(
        param, from_time=from_time, to_time=to_time, limit=limit
    )

    if len(data) == 0:
        error = "Нет данных"
        labels = ""
        data = []
    else:
        error = False
        prep = [x for x in zip(*data)]
        labels = prep[0]
        data = prep[1]
    return error, data, labels


def check_videorecord():
    my_cron = CronTab(user="pi")
    for job in my_cron:
        if job.comment == "Growbox":
            return True
    return False


def is_connected():
    remote_server = "https://www.google.com"
    try:
        response = requests.get(remote_server)
        # If response not successful, raise exception
        response.raise_for_status()
    except HTTPError as http_err:
        views_logger.error("is_connected: HTTP error", http_err)
        return False
    except Exception as err:
        views_logger.error("is_connected: Other error", err)
    else:
        views_logger.info("is_connected: Success connection")
        return True
