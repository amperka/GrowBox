#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template, make_response, request
import datetime, random
from get_data_from_database import get_hist_data
import serial_port, multiprocessing
import json


app = Flask(__name__)

#return index page
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

#return measurements page
@app.route("/measurements")
def measurements():
    return render_template("measurements/measurements.html")

#return temperature page with dynamic measurements
###############################################
@app.route("/measurements/temp")
def temp():
    template_data = {'label' : "Температура"}
    return render_template("measurements/temp.html", **template_data)

@app.route("/temp_measure")
def temp_meas():
    tp = serial_port.get_data_from_serial(output_queue)[0]
    return tp
################################################
#return humidity page with dynamic measurements
@app.route("/measurements/humidity")
def hum():
    template_data =  {'label' : "Влажность"}
    return render_template("measurements/humidity.html", **template_data)
@app.route("/hum_measure")
def hum_meas():
    hum = serial_port.get_data_from_serial(output_queue)[1]
    return hum
#################################################
#return pH page
@app.route("/measurements/ph")
def ph():
    template_data = {'label' : "Уровень pH"}
    return render_template("measurements/ph.html", **template_data)
@app.route("/ph_measure")
def ph_meas():
    ph = serial_port.get_data_from_serial(output_queue)[2]
    return ph
#################################################
#return TDS updatePage
@app.route("/measurements/tds")
def tds():
    template_data = {'label' : "Уровень солей"}
    return render_template("measurements/tds.html", **template_data)
@app.route("/tds_measure")
def tds_meas():
    tds = serial_port.get_data_from_serial(output_queue)[3]
    return tds
#################################################
#return CO2 page
@app.route("/measurements/co2")
def co2():
    template_data =  {'label' : "Уровень CO2"}
    return render_template("measurements/co2.html", **template_data)
@app.route("/co2_measure")
def co2_meas():
    co2 = serial_port.get_data_from_serial(output_queue)[4]
    return co2
##################################################

#camera control
@app.route("/camera")
def camera():
    return render_template("camera/camera.html")

@app.route("/camera/photo")
def photo():
    return render_template("camera/photo.html")

@app.route("/camera/video")
def video():
    return render_template("camera/video.html")

#return setting of GrowBox
@app.route("/settings")
def settings():
    return render_template("settings.html")

#return net_settings
@app.route("/net_settings")
def net_settings():
    return render_template("net_settings.html")

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
    return render_template("info.html")

@app.route("/dynamicCharts")
def dynamicTemp():
    return render_template("dynamicCharts.html")


if __name__ == "__main__":
    temp, hum, ph, tds, co2 = (0, 0, 0, 0, 0)
    output_queue = multiprocessing.Queue(2)

    sp = serial_port.SerialProcess(output_queue, "/dev/ttyACM0")
    sp.daemon = True

    sp.start()
    app.run(host='0.0.0.0', debug=False)
