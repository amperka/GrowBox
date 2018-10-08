#!/usr/bin/python3
from flask import Flask, render_template, make_response, request
import datetime
from getDataFromDatabase import getData, getHistData


app = Flask(__name__)

#return index page
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

#return setting of GrowBox
@app.route("/settings")
def settings():
    return render_template("settings.html")

#return measurement page
@app.route("/measurements")
def measurements():
    return render_template("measurements.html")

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
    hum, temp = (60, 30) #temporally
    return str(temp) + ' ' + str(hum)
################################################

#return pH page
@app.route("/ph")
def ph():
    return render_template("ph.html")

#return CO2 page
@app.route("/co2")
def co2():
    return render_template("co2.html")

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
    app.run(host='127.0.0.1', debug=True)
