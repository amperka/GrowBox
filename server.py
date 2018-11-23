#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template, make_response, request, Markup, Response
import os, datetime, random, json, time, sys
from datetime import datetime
import serial_port, multiprocessing, threading
import sqlite
import signal

WINDOWS = False
import platform
if platform.system() == 'Windows':
    WINDOWS = True

if not WINDOWS:
    from picamera import PiCamera

temp, hum, ph, tds, co2, lvl = ('0', '0', '0', '0', '0', '0')
input_queue = multiprocessing.Queue(1)

dbPeriod = 600 # seconds 
arrayLen = 10 
circularArray = [0] * arrayLen 
arrayPivot = 0 
itemPeriod = dbPeriod / arrayLen # seconds

app = Flask(__name__)
sql = sqlite.Sqlite('./database/sensorsData')

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
    template_data = {'label' : "Температура"}
    return render_template("measurements/temp.html", **template_data, goback='/measurements')

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
    template_data = {'label' : "Уровень солей"}
    return render_template("measurements/tds.html", **template_data, goback='/measurements')
@app.route("/tds_measure")
def tds_meas():
    with lock:
        ret_val = str(tds)
    return ret_val
#################################################
#return CO2 page
@app.route("/measurements/co2")
def co2():
    template_data =  {'label' : "Уровень CO2"}
    return render_template("measurements/co2.html", **template_data, goback='/measurements')
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
    return render_template("camera/camera.html", goback='/index')

@app.route("/camera/photo")
def photo():
    return render_template("camera/photo.html", goback='/index')

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
    return render_template("camera/video.html")

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

    #settingFile = open("settings.txt", "r")
    #data = Markup(settingFile.readline())
    #settingFile.close()
    return render_template("/settings/settings.html", jsonStr=data, title='Управление', goback='/index')

@app.route("/accept_settings", methods=["POST"])
def accept_setting():
    content = request.json
    input_queue.put(str(content))

    sql.updateActivity(str(content))

    #settingsFile = open("settings.txt", 'w')
    #settingsFile.write(str(content))
    #settingsFile.close()
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
    #input_queue.put(
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

###################################################

#return charts page
@app.route("/charts")
def charts():
    return render_template("charts/charts.html", title='Журнал', goback='/index')

#return chart for 30 days
@app.route("/charts/temp_chart")
def temp_chart():
    now = int(datetime.timestamp(datetime.now()))
    monthEarlier = now - 2592000
    data = sql.selectSensors(fromTime = monthEarlier, toTime = now, limit=30)
    error, data, labels = prepareData2Chart(data)
    label = "Температура"
    banner = "температуры"
    template_data = {'error': error, 'labels': labels, 'data': data, 'label': label, 'banner': banner}
    return render_template("charts/month_chart.html", title='Журнал температуры', goback='/charts', **template_data)

@app.route("/charts/hum_chart")
def hum_chart():
    now = int(datetime.timestamp(datetime.now()))
    monthEarlier = now - 2592000
    data = sql.selectSensors(fromTime = monthEarlier, toTime = now, limit=30)
    error, data, labels = prepareData2Chart(data)
    label = "Влажность"
    banner = "влажности"
    template_data = {'error': error, 'labels': labels, 'data': data, 'label': label, 'banner': banner}
    return render_template("charts/month_chart.html", title='Журнал влажности', goback='/charts', **template_data)

@app.route("/charts/ph_chart")
def ph_chart():
    now = int(datetime.timestamp(datetime.now()))
    monthEarlier = now - 2592000
    data = sql.selectSensors(fromTime = monthEarlier, toTime = now, limit=30)
    error, data, labels = prepareData2Chart(data)
    label = "Уровень кислотности pH"
    banner = "уровня кислотности pH"
    template_data = {'error': error, 'labels': labels, 'data': data, 'label': label, 'banner': banner}
    return render_template("charts/month_chart.html", title='Журнал уровня кислотности', goback='/charts', **template_data)

@app.route("/charts/tds_chart")
def tds_chart():
    now = int(datetime.timestamp(datetime.now()))
    monthEarlier = now - 2592000
    data = sql.selectSensors(fromTime = monthEarlier, toTime = now, limit=30)
    error, data, labels = prepareData2Chart(data)
    label = "Уровень солей"
    banner = "уровня солей"
    template_data = {'error': error, 'labels': labels, 'data': data, 'label': label, 'banner': banner}
    return render_template("charts/month_chart.html", title='Журнал уровня солей', goback='/charts', **template_data)

@app.route("/charts/co2_chart")
def co2_chart():
    now = int(datetime.timestamp(datetime.now()))
    monthEarlier = now - 2592000
    data = sql.selectSensors(fromTime = monthEarlier, toTime = now, limit=30)
    error, data, labels = prepareData2Chart(data)
    label = "Уровень CO2"
    banner = "уровня CO2"
    template_data = {'error': error, 'labels': labels, 'data': data, 'label': label, 'banner': banner}
    return render_template("charts/month_chart.html", title='Журнал концентрации углекислого газа', goback='/charts', **template_data)


#return return page about plants
@app.route("/info")
def info():
    return render_template("info.html", title='Справка', goback='/index')

@app.route("/dynamicCharts")
def dynamicTemp():
    return render_template("dynamicCharts.html")

def prepareData2Chart(data):
    print('DATA length: ' + str(len(data)))
    if len(data) == 0:
        error = "Нет данных"
        labels = ""
        data = []
    else:
        error = False
        prep = [x for x in zip(*data)]
        labels = [datetime.fromtimestamp(x).strftime("%m-%d %H:%M") for x in prep[0]]
        data = prep[1]
    return error, data, labels

def get():
    global temp, hum, ph, tds, co2, lvl
    global arrayPivot, arrayLen, circularArray
    
    
    arduino_path = auto_detect_serial()
    if arduino_path is not None:
        #sp = serial_port.SerialPort(arduino_path)
        if not WINDOWS:
            sp = serial_port.SerialPort(arduino_path)
        else:
            sp = serial_port.SerialPort("COM8")
    else:
        print("Arduino not connected")
        sys.exit(1)
    print("Arduino path is ", arduino_path) #testing
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
            hum = '0' 
            circularArray[arrayPivot] = (float(temp), float(hum), float(ph), float(tds), float(co2))
        arrayPivot += 1 
        if arrayPivot == arrayLen: 
            s = tuple([sum(x)/arrayLen for x in zip(*circularArray)])
            sql.insertSensors(s[0], s[1], s[2], s[3], s[4])
            arrayPivot = 0
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
    
    settings_file = open("settings.txt", "r")
    current_state = settings_file.readline()
    settings_file.close()
    input_queue.put(current_state)

    print("IS IT WINDOWS? -" + str(WINDOWS))


    lock = threading.Lock()
    getThread = threading.Thread(target=get)
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
