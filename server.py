#!/usr/bin/python3
from flask import Flask, render_template, make_response, request
import datetime, random
from getDataFromDatabase import getData, getHistData
import serialPort, multiprocessing


app = Flask(__name__)

#return index page
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

#return measurement page
@app.route("/measurements")
def measurements():
    return render_template("measurements/measurements.html")
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

@app.route("/charts/tempChart")
def tempChart():
    labels = [i for i in range(30)]
    tempData = getHistData(30)[1]
    templateData = {'labels' : labels, 'temp' : tempData}
    return render_template("charts/tempChart.html", **templateData)

@app.route("/charts/humChart")
def humChart():
    labels = [i for i in range(30)]
    humData = getHistData(30)[2]
    templateData = {'labels' : labels, 'hum' : humData}
    return render_template("charts/humChart.html", **templateData)

@app.route("/plot")
def imagePlot():
    labels = [i for i in range(500)]
    tempData = (getHistData(500))[1]
    humData = (getHistData(500))[2]
    templateData = {'labels':labels, 'temp':tempData, 'hum':humData}
    return render_template("plot.html", **templateData)

#return temperature page with dynamic measurements
###############################################
@app.route("/measurements/temp")
def temp():
    return render_template("measurements/temp.html")
@app.route("/dynamicCharts")
def dynamicTemp():
    return render_template("dynamicCharts.html")

@app.route("/tempmeas")
def temp_meas():
    tp = serialPort.getDataFromSerial(output_queue)[0]
    return tp
################################################
#return humidity renewTempPage
@app.route("/measurements/humidity")
def hum():
    return render_template("measurements/humidity.html")
@app.route("/hummeas")
def hum_meas():
    hum = serialPort.getDataFromSerial(output_queue)[1]
    return hum

#return pH page
@app.route("/measurements/ph")
def ph():
    return render_template("measurements/ph.html")
@app.route("/phmeas")
def ph_meas():
    ph = serialPort.getDataFromSerial(output_queue)[2]
    return ph

#return TDS updatePage
@app.route("/measurements/tds")
def tds():
    return render_template("measurements/tds.html")
@app.route("/tdsmeas")
def tds_meas():
    tds = serialPort.getDataFromSerial(output_queue)[3]
    return tds

#return CO2 page
@app.route("/measurements/co2")
def co2():
    return render_template("measurements/co2.html")
@app.route("/co2meas")
def co2_meas():
    co2 = serialPort.getDataFromSerial(output_queue)[4]
    return co2

#return return page about plants
@app.route("/info")
def info():
    return render_template("info.html")


if __name__ == "__main__":
    temp, hum, ph, tds, co2 = (0, 0, 0, 0, 0)

    output_queue = multiprocessing.Queue(5)
    sp = serialPort.SerialProcess(output_queue, "COM6")
    sp.daemon = True

    sp.start()
    app.run(host='127.0.0.1', debug=False)
