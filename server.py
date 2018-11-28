#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template, make_response, request, Markup, Response
import os, datetime, random, json, time, sys
from datetime import datetime
import serial_port, multiprocessing, threading
import sqlite
import signal
import random
import argparse

MOCK = False
if sys.argv[1] == '-mock':
    MOCK = True

WINDOWS = False
import platform
if platform.system() == 'Windows':
    WINDOWS = True

if ((not WINDOWS) and (not MOCK)):
    from picamera import PiCamera

temp, hum, ph, tds, co2, lvl = ('0', '0', '0', '0', '0', '0')
input_queue = multiprocessing.Queue(1)

# dbPeriod = 600 # seconds 
arrayLen = 10
requestPeriod = 1 # seconds
circularArray = [0] * arrayLen 
arrayPivot = 0 
# itemPeriod = dbPeriod / arrayLen # seconds

app = Flask(__name__)
sql = sqlite.Sqlite('./sensorsData.db')

#return index page
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title='Главная')

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
    template_data = {'label' : "Уровень pH"}
    return render_template("measurements/ph.html", **template_data, goback='/measurements')

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
        'title': "Уровень солей",
        'goback': "/measurements",
        'label' : "Уровень солей"
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
        'title': "Уровень CO2",
        'goback': "/measurements",
        'label' : "Уровень CO2"
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
    return render_template("camera/photo.html", title='Фото', goback='/camera')

@app.route("/make_photo/<img>")
def make_photo(img):
    camera = PiCamera()
    if img == "img1":
        name = "img1.jpg"
    elif img == "img2":
        name = "img2.jpg"
    camera.capture("./static/img/" + name, resize=(500, 300))
    camera.close()
    return render_template("camera/photo.html")

@app.route("/clear_photo")
def clear_photo():
    os.system("rm -f ./static/img/img*")
    return render_template("camera/photo.html")

@app.route("/camera/video")
def video():
    return render_template("camera/video.html", title='Видео', goback='/camera')

@app.route("/make_video")
def make_video():
    os.system("convert -delay 10 -loop 0 ./static/img/video_img/image* ./static/img/animation.gif")
    return render_template("/camera/video.html")

##################################################

#return setting of GrowBox
@app.route("/settings")
def settings():
    row = sql.selectActivity()
    data = Markup(row[0][0])
    return render_template("/settings/settings.html", jsonStr=data, title='Управление', goback='/index')

@app.route("/accept_settings", methods=["POST"])
def accept_setting():
    print(request)
    content = request.json
    print(content)
    input_queue.put(str(content))
    print('input')
    sql.updateActivity(str(content))
    print('sql')
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
####################################################

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'

@app.route("/net_setting", methods=["POST"])
def log_in():
    login = request.form["login"]
    passwd = request.form["passwd"]
    if check_auth(login, passwd):
        return render_template("/settings/teacher_settings.html", title='Настройки сети', goback='/index')
    return str("You are not loggined") #testing

@app.route("/login")
def secret_page():
    return render_template('/settings/login.html', title='Регистрация', goback='/index')

@app.route("/apply_net_settings", methods=["POST"])
def apply_net_settings():
    login = request.form["login"]
    passwd = request.form["passwd"]
    connect_flag = False
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "r+") as file:
        for line in file:
            if login in line:
                connect_flag = True
        if not connect_flag:
            file.write('\nnetwork={\n\tssid="'+ login +'"\n\tpsk="' + passwd + '"\n\tkey_mgmt=WPA-PSK\n}\n')
    if not connect_flag:
        os.system("wpa_cli -i wlan0 reconfigure")
    return render_template("/settings/teacher_settings.html", title="Настройки сети", goback='/index')

@app.route("/apply_time", methods=["POST"])
def apply_time():
    content = request.json
    datetime = content["set-date"] + ' ' + content["set-time"]
    print(datetime) #testing
    set_systime(datetime)
    # TODO: send json string to Arduino
    #input_queue.put(
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

###################################################

#return charts page
@app.route("/charts")
def charts():
    return render_template("charts/charts.html", title='Журнал', goback='/index')

#return chart
@app.route("/charts/<param>")
def temp_chart(param):
    if param == 'temp':
        template_data = {'label': "Температура", 'banner': "температуры"}
        title = "Журнал температуры"
    if param == 'humidity':
        template_data = {'label': "Влажность", 'banner': "влажности"}
        title = "Журнал влажности"
    if param == 'acidity':
        template_data = {'label': "Уровень кислотности pH", 'banner': "уровня кислотности pH"}
        title = "Журнал уровня кислотности"
    if param == 'saline':
        template_data = {'label': "Уровень солей", 'banner': "уровня солей"}
        title = "Журнал уровня солей"
    if param == 'carbon':
        template_data = {'label': "Уровень CO2", 'banner': "уровня CO2"}
        title = "Журнал концентрации углекислого газа"
    print(title)
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

#return return page about plants
@app.route("/info")
def info():
    return render_template("info.html", title='Справка', goback='/index')

@app.route("/dynamicCharts")
def dynamicTemp():
    return render_template("dynamicCharts.html")

def prepareMonthData2Chart(param):
    now = int(datetime.timestamp(datetime.now()))
    monthEarlier = now - 2592000
    # error, data, labels = prepareData(param, monthEarlier, now, 2592000 / (requestPeriod * arrayLen))
    error, data, labels = prepareData(param, monthEarlier, now, 100)
    labels = [datetime.fromtimestamp(x).strftime("%d.%m") for x in labels]
    return error, data, labels

def prepareWeekData2Chart(param):
    now = int(datetime.timestamp(datetime.now()))
    weekEarlier = now - 604800
    # error, data, labels = prepareData(param, weekEarlier, now, 604800 / (requestPeriod * arrayLen))
    error, data, labels = prepareData(param, weekEarlier, now, 50)
    labels = [datetime.fromtimestamp(x).strftime("%d.%m %Hh") for x in labels]
    return error, data, labels

def prepareDayData2Chart(param):
    now = int(datetime.timestamp(datetime.now()))
    dayEarlier = now - 86400
    # error, data, labels = prepareData(param, dayEarlier, now, 86400 / (requestPeriod * arrayLen))
    error, data, labels = prepareData(param, dayEarlier, now, 20)
    labels = [datetime.fromtimestamp(x).strftime("%H:%M") for x in labels]
    return error, data, labels

def prepareHourData2Chart(param):
    now = int(datetime.timestamp(datetime.now()))
    hourEarlier = now - 3600
    # error, data, labels = prepareData(param, hourEarlier, now, 3600 / (requestPeriod * arrayLen))
    error, data, labels = prepareData(param, hourEarlier, now, 5)
    labels = [datetime.fromtimestamp(x).strftime("%H:%M") for x in labels]
    return error, data, labels

def prepareData(param, fromTime, toTime, limit):
    data = sql.selectSensors(param, fromTime = fromTime, toTime = toTime, limit = limit)

    #print('DATA length: '+str(len(data)))
    if len(data) == 0:
        error = "Нет данных"
        labels = ""
        data = []
    else:
        for i in data:
            print(i)
        error = False        
        prep = [x for x in zip(*data)]
        labels = prep[0]
        data = prep[1]
    return error, data, labels

def insertSensorsIntoDB(temp, hum, ph, tds, co2, lvl):
    global arrayPivot, arrayLen, circularArray

    circularArray[arrayPivot] = (float(temp), float(hum), float(ph), float(tds), float(co2))
    arrayPivot += 1 
    if arrayPivot == arrayLen: 
        s = tuple([sum(x)/arrayLen for x in zip(*circularArray)])
        sql.insertSensors(temp=s[0], humidity=s[1], carbon=s[4], acidity=s[2], saline=s[3], level=lvl)
        arrayPivot = 0

def mockArduino():
    global temp, ph, tds, co2, lvl

    while True:
        if not input_queue.empty():
            command_data = input_queue.get()
            print("Write data to serial " + command_data) #testing

        temp = round(random.uniform(20, 30), 2)
        ph = round(random.uniform(4, 10), 1)
        tds = round(random.uniform(500, 700))
        co2 = round(random.uniform(500, 1100))
        lvl = round(random.uniform(0.0, 1.0))
        insertSensorsIntoDB(temp, '0', ph, tds, co2, lvl)

        time.sleep(1)


def readArduino():
    global temp, hum, ph, tds, co2, lvl
    
    if not WINDOWS:
        arduino_path = auto_detect_serial()
        if arduino_path is not None:
            sp = serial_port.SerialPort(arduino_path)
        else:
            print("Arduino not connected")
            sys.exit(1)
    else:
        arduino_path = "COM8"
        sp = serial_port.SerialPort(arduino_path)

    print("Arduino path is", arduino_path) #testing
    sp.open()
    data = {"temp" : 0, "carb" : 0, "acid" : 0, "salin" : 0, "level" : 0}
    empty_loop_count = 0
    while True:
        try:
            if not input_queue.empty():
                command_data = input_queue.get()
                sp.write_serial(command_data.encode())
                print("Write data to serial " + command_data) #testing

            while sp.serial_available():
                empty_loop_count = 0
                data = json.loads(sp.read_serial())
                #print(data) #testing
            empty_loop_count += 1
            if empty_loop_count > 10:
                raise Exception("Time is over")
        except:
            sp.close()
            print("Serial port disconnect")
            print("Try to reconnect")
            time.sleep(10) #testing
            arduino_path = auto_detect_serial()
            if arduino_path is not None:
                sp = serial_port.SerialPort(arduino_path)
            else:
                print("Arduino not connected")
                sys.exit(1)
            if sp.open():
                empty_loop_count = 0
                print("Connection succeful")
                input_queue.put(current_state)

        with lock:
            temp = data["temp"]
            ph = data["acid"]
            tds = data["salin"]
            co2 = data["carb"]
            lvl = data["level"]
            insertSensorsIntoDB(temp, '0', ph, tds, co2, lvl)

        time.sleep(1)

def auto_detect_serial():
    import glob
    path = glob.glob("/dev/ttyACM*")
    if len(path) > 0:
        return path[0]
    else:
        return None

def set_systime(datetime):
    os.system("sudo date --set='" + datetime + "'")

if __name__ == "__main__":

    sql.create()
    sql.createActivity()
    
    row = sql.selectActivity()
    data = Markup(row[0][0])
    input_queue.put(data)

    print("IS IT WINDOWS? -" + str(WINDOWS))
    print("SHOULD MOCK? -" + str(MOCK))

    lock = threading.Lock()
    if MOCK:
        getThread = threading.Thread(target=mockArduino)
    else:
        getThread = threading.Thread(target=readArduino)
    getThread.daemon = True
    getThread.start()

    def sigint_handler(signum, frame):
        print("Stop pressing the CTRL+C!")
        # need to fix
        sp.close()
        getThread.join()
        print("Join the thread. Is it alive?")
        print(getThread.is_alive())
        print("Exit application")
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        sys.exit(1)

    signal.signal(signal.SIGINT, sigint_handler)
    app.run(host='0.0.0.0', debug=False, threaded=True)
