#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template, make_response, request, Markup
import os, datetime, random, json, time, sys
from get_data_from_database import get_hist_data
import serial_port, multiprocessing, threading
import sqlite
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
        ret_val = temp
    return ret_val
################################################
#return humidity page with dynamic measurements
@app.route("/measurements/humidity")
def hum():
    template_data =  {'label' : "Влажность"}
    return render_template("measurements/humidity.html", **template_data, goback='/measurements')
@app.route("/hum_measure")
def hum_meas():
    with lock:
        ret_val = hum 
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
        ret_val = ph
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
        ret_val = tds
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
        ret_val = co2
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
    #settings = {'curstate': row[0], 'lampMode': row[1], 'fanMode': row[2], 'comprMode': row[3]}
    data = Markup(row[0][0])

    #settingFile = open("settings.txt", "r")
    #data = Markup(settingFile.readline())
    #settingFile.close()
    return render_template("/settings/settings.html", jsonStr=data, title='Управление', goback='/index')

@app.route("/accept_settings", methods=["POST"])
def accept_setting():
    content = request.json
    #input_queue.put('{"lamp":[1, 18]}')    
    input_queue.put(str(content))

    sql.updateActivity(str(content))

    #settingsFile = open("settings.txt", 'w')
    #settingsFile.write(str(content))
    #settingsFile.close()
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

#return net_settings
@app.route("/net_settings")
def net_settings():
    return render_template("/settings/net_settings.html")

###################################################


#return charts page
@app.route("/charts")
def charts():
    return render_template("charts/charts.html")

#return chart for 30 days
@app.route("/charts/temp_chart")
def temp_chart():
    labels = [i for i in range(30)]
    data = get_hist_data(30)[1]
    label = "Температура"
    banner = "температуры"
    template_data = {'labels' : labels, 'data' : data, 'label': label, 'banner' : banner}
    return render_template("charts/month_chart.html", **template_data)

@app.route("/charts/hum_chart")
def hum_chart():
    labels = [i for i in range(30)]
    data = get_hist_data(30)[2]
    label = "Влажность"
    banner = "влажности"
    template_data = {'labels' : labels, 'data' : data, 'label' : label, 'banner' : banner}
    return render_template("charts/month_chart.html", **template_data)

@app.route("/charts/ph_chart")
def ph_chart():
    labels = [i for i in range(30)]
    data = [i for i in range(30)] #temporally
    label = "Уровень pH"
    banner = "уровня pH"
    template_data = {'labels' : labels, 'data' : data, 'label' : label, 'banner' : banner}
    return render_template("charts/month_chart.html", **template_data)

@app.route("/charts/tds_chart")
def tds_chart():
    labels = [i for i in range(30)]
    data = [i for i in range(30)] #temporally
    label = "Уровень солей"
    banner = "уровня солей"
    template_data = {'labels' : labels, 'data' : data, 'label' : label, 'banner' : banner}
    return render_template("charts/month_chart.html", **template_data)

@app.route("/charts/co2_chart")
def co2_chart():
    labels = [i for i in range(30)]
    data = [i for i in range(30)] #temporally
    label = "Уровень CO2"
    banner = "уровня CO2"
    template_data = {'labels' : labels, 'data' : data, 'label' : label, 'banner' : banner}
    return render_template("charts/month_chart.html", **template_data)


#return return page about plants
@app.route("/info")
def info():
    return render_template("info.html", title='Справка', goback='/index')

@app.route("/dynamicCharts")
def dynamicTemp():
    return render_template("dynamicCharts.html")

def get():
    global temp, hum, ph, tds, co2
    global arrayPivot, arrayLen, circularArray
    data = "0 0 0 0 0 0"
    empty_loop_count = 0
    while True:
        if not input_queue.empty():
            command_data = input_queue.get()
            sp.write_serial(command_data.encode())
            print("Write data to serial " + command_data) #testing

        while sp.serial_available():
            empty_loop_count = 0
            data = sp.read_serial()
        empty_loop_count += 1
        if empty_loop_count > 10:
            sp.close()
            print("Serial port disconnect")
            sys.exit(1)
        with lock:
            temp, hum, ph, tds, co2, lvl = data.split() 
            circularArray[arrayPivot] = (float(temp), float(hum), float(ph), float(tds), float(co2))
        arrayPivot += 1 
        if arrayPivot == arrayLen: 
            s = tuple([sum(x)/arrayLen for x in zip(*circularArray)])
            sql.insertSensors(s[0], s[1], s[2], s[3], s[4])
            arrayPivot = 0
        time.sleep(1)



if __name__ == "__main__":

    sql.create()
    sql.createActivity()
    
    sp = serial_port.SerialPort("/dev/ttyACM0")
    sp.open()

    lock = threading.Lock()
    getThread = threading.Thread(target=get)
    getThread.daemon = True
    getThread.start()

    settings_file = open("settings.txt", "r")
    current_state = settings_file.readline()
    settings_file.close()
    input_queue.put(current_state)

    app.run(host='0.0.0.0', debug=False)
