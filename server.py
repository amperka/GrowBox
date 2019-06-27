#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template, make_response, request, Markup, Response
import os, datetime, random, json, time, sys, shutil
from datetime import datetime
import serial_port, threading, queue
import sqlite
import signal
import subprocess
import logging
import random
import requests
from requests.exceptions import HTTPError

sys.path.append('/home/pi/.local/lib/python3.5/site-packages')
os.chdir("/home/pi/Projects/Test1/GrowBox/") #for autostart change path

import usb_camera
from crontab import CronTab

app = Flask(__name__) #Flask application


#return index page
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title='Главное меню', lock='/lock')


#return measurements page
@app.route("/measurements")
def measurements():
    return render_template("measurements/measurements.html", title='Измерения', goback='/index')


#return temperature page with dynamic measurements
###############################################

@app.route("/measurements/temp")
def temp():
    template_data = {
        'title': "Температура",
        'goback': "/measurements",
        'label' : "Температура"
    }
    return render_template("measurements/temp.html", **template_data)

@app.route("/temp_measure")
def temp_meas():
    with lock:
        ret_val = str(temp)
    return ret_val


#################################################
#return pH page
@app.route("/measurements/ph")
def ph():
    template_data = {
            'title' : "Уровень pH",
            'label' : "Уровень pH",
            'goback': "/measurements",
    }
    return render_template("measurements/ph.html", **template_data)

@app.route("/ph_measure")
def ph_meas():
    with lock:
        ret_val = str(ph)
    return ret_val
#################################################
#return TDS updatePage
@app.route("/measurements/tds")
def tds():
    template_data = {
        'title': "Солёность",
        'goback': "/measurements",
        'label' : "Уровень солей",
    }
    return render_template("measurements/tds.html", **template_data)

@app.route("/tds_measure")
def tds_meas():
    with lock:
        ret_val = str(tds)
    return ret_val
#################################################
#return CO2 page
@app.route("/measurements/co2")
def co2():
    template_data =  {
        'title': "Углекислый газ",
        'goback': "/measurements",
        'label' : "CO2",
    }
    return render_template("measurements/co2.html", **template_data)

@app.route("/co2_measure")
def co2_meas():
    with lock:
        ret_val = str(co2)
    return ret_val
##################################################

#camera control
##################################################
@app.route("/camera")
def camera():
    return render_template("camera/camera.html", title='Камера', goback='/index')

@app.route("/camera/photo")
def photo():
    img1_exist = os.path.isfile("./static/img/img1.jpg")
    img2_exist = os.path.isfile("./static/img/img2.jpg")
    img1_name = "img1.jpg?" + str(random.random())
    img2_name = "img2.jpg?" + str(random.random())
    if img1_exist and img2_exist:
        template_data = {
            'img1' : img1_name,
            'img2' : img2_name,
            'pad1' : "0px",
            'pad2' : "0px",
        }
    elif img1_exist and not img2_exist:
        template_data = {
            'img1' : img1_name,
            'img2' : "Camera.png",
            'pad1' : "0px",
            'pad2' : "50px 120px",
        }
    elif not img1_exist and img2_exist:
        template_data = {
            'img1' : "Camera.png",
            'img2' : img2_name,
            'pad1' : "50px 120px",
            'pad2' : "0px"
        }
    else:
        template_data = {
            'img1' : "Camera.png",
            'img2' : "Camera.png",
            'pad1' : "50px 120px",
            'pad2' : "50px 120px",
        }
    return render_template("camera/photo.html", title='Фото', goback='/camera', **template_data)


@app.route("/make_photo/<img>")
def make_photo(img):
    camera = usb_camera.PiCamera(0)
    if img == "img1":
        name = "img1.jpg"
    elif img == "img2":
        name = "img2.jpg"
    try:
        camera.capture("./static/img/" + name, resize=(480, 320))
    except RuntimeError:
        logger.error("Photo is not created")
        return make_response('', 403)
    else:
        return make_response('', 200)
    finally:
        logger.debug("Camera close") #test
        camera.close()

@app.route("/clear_photo")
def clear_photo():
    os.system("rm -f ./static/img/img*")
    return make_response('', 200)


@app.route("/camera/video")
def video():
    record_status = check_videorecord()
    if record_status:
        print("Videorecord is on") #testing
        record_message = "Остановить запись"
    else:
        print("Videorecord is off") #testing
        record_message = "Включить запись"
    video_exist = os.path.isfile("./static/img/timelapse.mp4")
    video_path = "/static/img/timelapse.mp4?" + str(random.random())
    template_data = {
                'title' : "Видео",
                'goback' : "/camera",
                'recStatus': record_status,
                'recMess' : record_message,
                'videoExist' : video_exist,
                'videoPath' : video_path,
    }
    return render_template("camera/video.html", **template_data)


@app.route("/start_record")
def start_record():
    try:
        camera = usb_camera.PiCamera(0)
        if not camera.check_connection():
            raise RuntimeError
    except RuntimeError:
        logger.error("Camera is not connected")
        return make_response('', 403)
    finally:
        camera.close()
    my_cron = CronTab(user="pi")
    for job in my_cron:
        if job.comment == "Growbox":
            print("Too many clicks") #testing
            return make_response('', 403)
    job = my_cron.new(command="/home/pi/Projects/Test1/GrowBox/usb_camera.py", comment="Growbox") #there will be new path
    job.every(1).hours()
    print(job) #testing
    my_cron.write()
    return make_response('', 200)


@app.route("/finish_record")
def finish_record():
    my_cron = CronTab(user="pi")
    for job in my_cron:
        if job.comment == "Growbox":
            my_cron.remove(job)
            my_cron.write()
            return make_response('', 200)
    return make_response('', 403)


@app.route("/remove_frames")
def remove_frames():
    if len(os.listdir("/home/pi/Pictures")) == 0:
        print("Pictures directory is empty")
        return make_response('', 403)
    try:
        command = "rm -f /home/pi/Pictures/*"
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as err:
        print("Error", err) #testing
        return make_response('', 403)
    else:
        print("Remove frame OK") #testing
        return make_response('', 200)


@app.route("/remove_video")
def remove_video():
    if os.path.exists("./static/img/timelapse.mp4"):
        try:
            subprocess.run(["rm", "-f", "./static/img/timelapse.mp4"], check=True)
        except subprocess.CalledProcessError as err:
            print("Error", err) #testing
            return make_response('', 403)
        else:
            print("Remove video OK") #testing
            return make_response('', 200)
    print("File not exist, nothing to delete")
    return make_response('', 403)


@app.route("/make_video")
def make_video():
    if len(os.listdir("/home/pi/Pictures")) != 0:
        command = ["ffmpeg", "-y", "-r", "10", "-i", "/home/pi/Pictures/%*.jpg", "-r",
                   "10", "-vcodec", "libx264", "-vf", "scale=480:320", "./static/img/timelapse.mp4"]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as err:
            logger.error("Error", err) #testing
            return make_response('', 403)
        else:
            logger.debug("Video is created") #testing
            return make_response('', 200)
    return make_response('', 403)


##################################################


############## GrowBox settings ##################


@app.route("/settings")
def settings():
    row = sql.selectActivity()
    data = Markup(row[0][0])
    return render_template("/settings/settings.html", jsonStr=data, title='Управление', goback='/index')

@app.route("/accept_settings", methods=["POST"])
def accept_setting():
    content = request.json
    input_queue.put(str(content))
    sql.updateActivity(str(content))
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


###################################################


############## Teacher settings ###################


@app.route("/login")
def secret_page():
    return render_template('/settings/login.html', title='Регистрация', goback='/index')


@app.route("/lock")
def lock():
    return render_template('/lock.html')


@app.route("/teacher_settings", methods=["POST"])
def log_in():
    content = request.json
    passwd = content["passwd"]
    if passwd == "2486":
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    return make_response('', 403)


@app.route("/teacher_page")
def teacher_page():
    return render_template('/settings/teacher_settings.html', title='Настройки', goback='/index')


@app.route("/teacher_page/<settings>")
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
    template_data = {
        'title' : title,
        'goback' : "/teacher_page",
    }
    return render_template(ret_val, **template_data)


@app.route("/apply_net_settings", methods=["POST"])
def apply_net_settings():
    content = request.json
    login = content["login"]
    passwd = content["passwd"]
    print(login, passwd)

    settings_str = ("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n" +
                    "update_config=1\n" +
                    "country=RU\n")
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as file:
        file.write(settings_str)
        file.write('\nnetwork={\n\tssid="'+ login +'"\n\tpsk="' + passwd + '"\n\tkey_mgmt=WPA-PSK\n}\n')

    os.system("wpa_cli -i wlan0 reconfigure")
    time.sleep(10)
    if is_connected():
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success':False}), 403, {'ContentType':'application/json'}


@app.route("/update_system")
def update_system():
    if not is_connected():
        return make_response('', 403)
    ret = os.system("echo Update") #testing
    time.sleep(5) #testing
    #ret = os.system("git pull origin master") #uncomment to update
    if ret == 0:
        logger.info("System update")
        return make_response('', 200)
    else:
        return make_response('', 403)


@app.route("/apply_time", methods=["POST"])
def apply_time():
    content = request.json
    date = content["set-date"]
    time = content["set-time"]
    date = '-'.join(date.split('-')[::-1]) #reverse string from %dd-%mm-%yyyy to %yyyy-%mm-%dd
    datetime_set = date + ' ' + time
    set_systime(datetime_set)
    datetime_obj = datetime.strptime(datetime_set, "%Y-%m-%d %H:%M")
    fmt_datetime = {"setTime"  : datetime_obj.strftime("%a %b %d %H:%M:%S %Y")}
    input_queue.put(json.dumps(fmt_datetime))
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route("/calibration/<param>")
def calibration(param):
    if param == "four":
        command = json.dumps({"calibrate" : 4})
        print(command)
        input_queue.put(command)
    if param == "seven":
        command = json.dumps({"calibrate" : 7})
        print(command)
        input_queue.put(command)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route("/download_log")
def download_log():
    media_dir = os.listdir("/media/pi")
    if len(media_dir) == 0:
        logger.error("download_log: USB-device not found")
        return make_response('', 403)
    usb_path = "/media/pi/" + media_dir[0]
    try:
        shutil.copy("./growbox.log", usb_path)
    except Exception as e:
        logger.error("Something go wrong") #testing
        return make_response('', 403)
    return make_response('', 200)


@app.route("/extract_usb")
def extract_usb():
    media_dir = os.listdir("/media/pi")
    if len(media_dir) == 0:
        logger.error("extract_usb: USB-device not found")
        return make_response('', 403)
    command = ['sudo', 'umount', '/dev/sda1']
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as err:
        print("Something go wrong", err) #testing
        return make_response('', 403)
    return make_response('', 200)


@app.route("/shutdown/<param>")
def shutdown(param):
    stop_ser_thread()
    shutdown_server = request.environ.get('werkzeug.server.shutdown')
    if shutdown_server is None:
        raise RuntimeError("Shutdown server is not available")
    else:
        shutdown_server()
        if param == "reboot":
            os.system("sleep 20 && sudo reboot &")
            return make_response('', 200)
        elif param == "shutdown":
            os.system("sleep 20 && sudo shutdown -h now &")
            return make_response('', 200)

###################################################

################ Charts pages #####################


@app.route("/charts")
def charts():
    return render_template("charts/charts.html", title='Журнал', goback='/index')


@app.route("/charts/<param>")
def temp_chart(param):
    if param == 'temp':
        template_data = {'label': "Температура", 'banner': "температуры"}
        title = "Журнал температуры"
    if param == 'acidity':
        template_data = {'label': "Уровень кислотности pH", 'banner': "уровня кислотности pH"}
        title = "Журнал уровня кислотности"
    if param == 'saline':
        template_data = {'label': "Уровень солей", 'banner': "уровня солей"}
        title = "Журнал уровня солей"
    if param == 'carbon':
        template_data = {'label': "Уровень CO2", 'banner': "уровня CO2"}
        title = "Журнал концентрации углекислого газа"
    return render_template("charts/month_chart.html", param=param, title=title, goback='/charts', **template_data)


@app.route("/charts/draw_chart", methods=["POST"])
def draw_chart():
    if request.json:
        param = request.json['param']
        period = request.json['period']
        if period:
            if period == 'hour':
                error, data, labels = prepareHourData2Chart(param = [param])
            if period == 'day':
                error, data, labels = prepareDayData2Chart(param = [param])
            if period == 'week':
                error, data, labels = prepareWeekData2Chart(param = [param])
            if period == 'month':
                error, data, labels = prepareMonthData2Chart(param = [param])

            template_data = {'error': error, 'labels': labels, 'data': data, 'param': param}
            return json.dumps(template_data), 200, {'ContentType':'application/json'}


###################################################

############## About plants #######################

@app.route("/info")
def info():
    return render_template("/info/info.html", title='Справка', goback='/index')

@app.route("/info/<plant>")
def select_plant(plant):
    ret_val = "/info/" + plant + ".html"
    if plant == "salad":
        title = "Салат"
    elif plant == "bean":
        title = "Фасоль"
    elif plant == "oats":
        title = "Oвёс"
    template_data = {
        'title': title,
        'goback': "/info",
    }
    return render_template(ret_val, **template_data)


@app.route("/dynamicCharts")
def dynamicTemp():
    return render_template("dynamicCharts.html")

def prepareMonthData2Chart(param):
    now = int(datetime.timestamp(datetime.now()))
    monthEarlier = now - 2592000
    error, data, labels = prepareData(param, monthEarlier, now, 2592000 // (requestPeriod * arrayLen))
    #error, data, labels = prepareData(param, monthEarlier, now, 100)
    labels = [datetime.fromtimestamp(x).strftime("%d.%m") for x in labels]
    return error, data, labels

def prepareWeekData2Chart(param):
    now = int(datetime.timestamp(datetime.now()))
    weekEarlier = now - 604800
    error, data, labels = prepareData(param, weekEarlier, now, 604800 // (requestPeriod * arrayLen))
    #error, data, labels = prepareData(param, weekEarlier, now, 50)
    labels = [datetime.fromtimestamp(x).strftime("%d.%m %Hh") for x in labels]
    return error, data, labels

def prepareDayData2Chart(param):
    now = int(datetime.timestamp(datetime.now()))
    dayEarlier = now - 86400
    error, data, labels = prepareData(param, dayEarlier, now, 86400 // (requestPeriod * arrayLen))
    #error, data, labels = prepareData(param, dayEarlier, now, 20)
    labels = [datetime.fromtimestamp(x).strftime("%H:%M") for x in labels]
    return error, data, labels

def prepareHourData2Chart(param):
    now = int(datetime.timestamp(datetime.now()))
    hourEarlier = now - 3600
    error, data, labels = prepareData(param, hourEarlier, now, 3600 // (requestPeriod * arrayLen))
    #error, data, labels = prepareData(param, hourEarlier, now, 5)
    labels = [datetime.fromtimestamp(x).strftime("%H:%M") for x in labels]
    return error, data, labels

def prepareData(param, fromTime, toTime, limit):
    data = sql.selectSensors(param, fromTime = fromTime, toTime = toTime, limit = limit)

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


def insertSensorsIntoDB(temp, ph, tds, co2, lvl):
    global arrayPivot, arrayLen, circularArray

    circularArray[arrayPivot] = (float(temp), float(ph), float(tds), float(co2))
    arrayPivot += 1
    if arrayPivot == arrayLen:
        s = tuple([round(sum(x)/arrayLen, 2) for x in zip(*circularArray)])
        sql.insertSensors(temp=s[0], carbon=s[3], acidity=s[1], saline=s[2], level=lvl)
        arrayPivot = 0


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
        #if response not successful, raise exception
        response.raise_for_status()
    except HTTPError as http_err:
        print("HTTP error", http_err)
        return False
    except Exception as err:
        print("Other error", err)
    else:
        print("Success connection")
        return True


def readArduino():
    global temp, ph, tds, co2, lvl

    arduino_path = auto_detect_serial()
    if arduino_path is not None:
        sp = serial_port.SerialPort(arduino_path)
    else:
        logger.error("Arduino not connected")
        sys.exit(1)

    print("Arduino path is", arduino_path) #testing
    sp.open()
    data = {"temp" : 0, "carb" : 0, "acid" : 0, "salin" : 0, "level" : 0}
    empty_loop_count = 0
    reconnect_count = 0
    first_data_pack_flag = False
    while True:
        try:
            if not input_queue.empty():
                command_data = input_queue.get()
                if command_data == "Exit":
                    break
                sp.write_serial(command_data.encode())
                logger.debug("Write data to serial " + command_data) #testing

            while sp.serial_available():
                empty_loop_count = 0
                data = json.loads(sp.read_serial())
                if not first_data_pack_flag:
                    reconnect_count = 0
                    current_time = datetime.fromtimestamp(data["time"])
                    set_systime(str(current_time))
                    first_data_pack_flag = True
            empty_loop_count += 1
            if empty_loop_count > 10:
                raise RuntimeError("Time is over")
        except (RuntimeError, OSError):
            sp.close()
            logger.error("Serial port disconnect")
            logger.info("Try to reconnect")
            reconnect_count += 1
            if reconnect_count > 3:
                logger.info("Reconnection limit. Please restart your computer.")
                sys.exit(1)
            time.sleep(10) #testing
            arduino_path = auto_detect_serial()
            if arduino_path is not None:
                sp = serial_port.SerialPort(arduino_path)
            else:
                logger.error("Arduino not connected")
                sys.exit(1)
            if sp.open():
                empty_loop_count = 0
                logger.info("Connection succeful")
                input_queue.put(current_state)

        with lock:
            temp = data["temp"]
            ph = data["acid"]
            tds = data["salin"]
            co2 = data["carb"]
            lvl = data["level"]
            insertSensorsIntoDB(temp, ph, tds, co2, lvl)

        time.sleep(1)
    sp.close()
    print("Serial port thread successfully terminated")

def auto_detect_serial():
    import glob
    path = glob.glob("/dev/ttyACM*")
    if len(path) > 0:
        return path[0]
    else:
        return None


def set_systime(datetime):
    os.system("sudo date --set='" + datetime + "'")


def stop_ser_thread():
    input_queue.put("Exit")
    getThread.join()

def sigint_handler(signum, frame):
    print("Process was terminated by pressing Ctrl+c")
    stop_ser_thread()
    print("Exit application")
    sys.exit(1)


if __name__ == "__main__":

    temp, ph, tds, co2, lvl = ('0', '0', '0', '0', '0')
    input_queue = queue.Queue(1)

    # dbPeriod = 600 # seconds
    arrayLen = 600
    requestPeriod = 1 # seconds
    circularArray = [0] * arrayLen
    arrayPivot = 0
    # itemPeriod = dbPeriod / arrayLen # seconds

    #create database for sensors and activities
    sql = sqlite.Sqlite('./sensorsData.db')

    #create own logger
    logger = logging.getLogger("server")
    logger.setLevel(logging.DEBUG)

    #create logging file handler
    file_handler = logging.FileHandler("growbox.log")
    date_format = "%Y-%m-%d %H:%M:%S"
    message_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(message_format, date_format)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("Server started")

    sql.create()
    sql.createActivity()
    row = sql.selectActivity()
    current_state = Markup(row[0][0])
    input_queue.put(current_state)

    lock = threading.Lock()

    #create and run Arduino thread
    getThread = threading.Thread(target=readArduino)
    getThread.daemon = True
    getThread.start()

    signal.signal(signal.SIGINT, sigint_handler)

    app.run(host='0.0.0.0', debug=False, threaded=True)
