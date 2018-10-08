#!/usr/bin/python3
from flask import Flask, render_template, make_response, request
import dht11_measurement
import Adafruit_DHT
import datetime
from getDataFromDatabase import getData, getHistData


app = Flask(__name__)

#return index page
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

#return temperature page with dynamic measurements
###############################################
@app.route("/temp")
def temp():
    return render_template("temp.html")
@app.route("/dynamicCharts")
def dynamicTemp():
    return render_template("dynamicCharts.html")

@app.route("/tempmeas")
def temp_meas():
    hum, temp = dht11_measurement.measurement(Adafruit_DHT.DHT11, 4)
    return str(temp) + ' ' + str(hum)
################################################

#return pH page 
@app.route("/ph")
def ph():
    return render_template("ph.html")

#return CO2 page 
@app.route("/co2")
def co2():
    return "There will be CO2 level"

@app.route("/info")
def info():
    return render_template("info.html")

@app.route("/tempDatabase")
def tempDatabase():
    time, temp, hum = getData()
    templateData = {'time':time, 'temp':temp, 'hum':hum}
    return render_template("tempDatabase.html", **templateData)

@app.route("/plot")
def imagePlot():
    labels = [i for i in range(500)]
    tempData = (getHistData(500))[1]
    humData = (getHistData(500))[2]
    templateData = {'labels':labels, 'temp':tempData, 'hum':humData}
    return render_template("plot.html", **templateData)        

if __name__ == "__main__":
    app.run(host='192.168.88.150', debug=True)

