#!/usr/bin/python3
import time
import sqlite3

dbname = '/home/pi/Projects/GrowBox/Sensors_Database/sensorsData.db'

#get data from DHT
def getDHTdata():
    hum, temp = (60, 30) #temporally

    if hum is not None and temp is not None:
        hum = round(hum)
        temp = round(temp, 1)
        logData(temp, hum)

#log sensor data on database
def logData(temp, hum):
    conn = sqlite3.connect(dbname)
    curs = conn.cursor()
    curs.execute("INSERT INTO DHT_data values(datetime('now'), (?), (?))", (temp, hum))
    conn.commit()
    conn.close()

#display database data
def displayData():
    conn = sqlite3.connect(dbname)
    curs = conn.cursor()
    print("Database content")
    for row in curs.execute("SELECT * FROM DHT_data"):
        print(row)
    conn.close

if __name__=="__main__":
    getDHTdata()
