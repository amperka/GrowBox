#!/usr/bin/python3
import time
import sqlite3
from datetime import datetime
import random

dbname = './sensorsData.db'

#create table activity
def createActivity():
    sql = "CREATE TABLE IF NOT EXISTS activity(curstate TEXT, lamp INT DEFAULT 1, fan INT DEFAULT 10, compressor INT DEFAULT 1)"
    conn = sqlite3.connect(dbname)
    curs = conn.cursor()
    curs.execute(sql)
    conn.commit()
    conn.close()

#test activity
def testActivity():

    curstate = random.randrange(-10, 30, 1)
    lamp = random.randrange(0, 100, 1)
    fan = random.randrange(0, 100, 1)
    compressor = random.randrange(0, 100, 1)

    print(curstate, lamp, fan, compressor)

    updateActivity(curstate, lamp, fan, compressor)

#update a row of activity
def updateActivity(curstate={}, lampMode=1, fanMode=10, compressorMode=1):

    lamp = str(int(lampMode))
    fan = str(int(fanMode))
    compressor = str(int(compressorMode))

    sql = "UPDATE activity SET curstate=?, lamp=?, fan=?, compressor=?"
    val = (curstate, lamp, fan, compressor)

    conn = sqlite3.connect(dbname)
    curs = conn.cursor()
    curs.execute(sql, val)
    conn.commit()
    conn.close()

#select from activity
def selectActivity():
    sql = "SELECT * FROM activity LIMIT -1"

    conn = sqlite3.connect(dbname)
    curs = conn.cursor()
    curs.execute(sql)
    rows = curs.fetchall()
    conn.close()
    return rows

#create table sensors
def create():
    sql = "CREATE TABLE IF NOT EXISTS sensors(date INT, temp REAL, humidity INT, carbon INT, acidity REAL, saline INT, level INT)"
    conn = sqlite3.connect(dbname)
    curs = conn.cursor()
    curs.execute(sql)
    conn.commit()
    conn.close()

#delete table sensors
def drop():
    sql = "DROP TABLE sensors"
    conn = sqlite3.connect(dbname)
    curs = conn.cursor()
    curs.execute(sql)
    conn.commit()
    conn.close()

#insert test row into sensors table
def testDataInsert():
    temp = random.randrange(-10, 30, 1)
    hum = random.randrange(0, 100, 1)
    carb = random.randrange(0, 1000, 10)
    acid = random.randrange(1, 15, 1)
    saline = random.randrange(0, 1000, 15)
    lvl = random.randint(0, 1)

    insertSensors(temp, hum, carb, acid, saline, lvl)

#insert a row into sensors
def insertSensors(temp='NULL', humidity='NULL', carbon='NULL', acidity='NULL', saline='NULL', level='NULL'):
    date = datetime.timestamp(datetime.now()) # FLOAT
    date = int(date) # INTEGER

    # print(date, temp, humidity, carbon, acidity, saline, level)

    sql = "INSERT INTO sensors(date, temp, humidity, carbon, acidity, saline, level) values(?, ?, ?, ?, ?, ?, ?)"
    val = (date, temp, humidity, carbon, acidity, saline, level)

    conn = sqlite3.connect(dbname)
    curs = conn.cursor()
    curs.execute(sql, val)
    conn.commit()
    conn.close()

#count rows in sensors table
def countSensors():

    sql = "SELECT COUNT(*) FROM sensors"

    conn = sqlite3.connect(dbname)
    curs = conn.cursor()
    curs.execute(sql)
    rows = curs.fetchall()
    conn.close()
    return rows[0][0]


#select dsensors data of [fromTime; toTime] period
def selectSensors(fromTime = None, toTime = None):

    sql = "SELECT * FROM sensors"
    if fromTime:
        sql = sql + " WHERE date>=" + str(int(fromTime))
        if toTime:
            sql = sql + " AND date<=" + str(int(toTime))

    # print(sql)

    conn = sqlite3.connect(dbname)
    curs = conn.cursor()
    curs.execute(sql)
    rows = curs.fetchall()
    conn.close()
    return rows

if __name__=="__main__":
    create()
    createActivity()

    #tests begin
    print('-----activity-----')
    testActivity()
    for row in selectActivity():
        print(row)
    print('-----sensors-----')
    testDataInsert()
    print(countSensors())
    now = datetime.timestamp(datetime.now())
    print('----------------')
    for row in selectSensors():
        print(row)
    print('----------------')
    for row in selectSensors(now-3600*4):
        print(row)
    print('----------------')
    for row in selectSensors(now-3600*6):
        print(row)
    print('----------------')
    for row in selectSensors(now-3600*10, now):
        print(row)
    print('----------------')
    #tests end
