#!/usr/bin/python3
import time
import sqlite3
from datetime import datetime
import random

class Sqlite():

    def __init__(self, dbFilename):
        self.dbname = dbFilename

    #create table activity
    def createActivity(self):
        sql = "CREATE TABLE IF NOT EXISTS activity(curstate TEXT, lamp INT DEFAULT 1, fan INT DEFAULT 10, compressor INT DEFAULT 1)"
        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql)
        conn.commit()
        conn.close()

        if len(self.selectActivity()) == 0:
            conn = sqlite3.connect(self.dbname)
            curs = conn.cursor()
            curs.execute("INSERT INTO activity(curstate) values('')")
            conn.commit()
            conn.close()

    #test activity
    def testActivity(self):

        curstate = str({'compressor': 0, 'fan': [0, 10], 'lamp': [1, 18]})
        lamp = random.randrange(0, 100, 1)
        fan = random.randrange(0, 100, 1)
        compressor = random.randrange(0, 100, 1)

        print(curstate, lamp, fan, compressor)        

        self.updateActivity(curstate, lamp, fan, compressor)

    #update a row of activity
    def updateActivity(self, curstate={}, lampMode=1, fanMode=10, compressorMode=1):

        lamp = str(int(lampMode))
        fan = str(int(fanMode))
        compressor = str(int(compressorMode))

        sql = "UPDATE activity SET curstate=?, lamp=?, fan=?, compressor=? WHERE 1=1"
        val = (curstate, lamp, fan, compressor)

        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql, val)
        conn.commit()
        conn.close()

    #select from activity
    def selectActivity(self):
        sql = "SELECT * FROM activity"

        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql)
        rows = curs.fetchall()
        conn.close()
        print(rows)
        return rows
        # return {'curstate': rows[0], 'lampMode': rows[1], 'fanMode': rows[2]}
        # return {'curstate': rows[0], 'lampMode': rows[1], 'fanMode': rows[2], 'comprMode': rows[3]}

    #create table sensors
    def create(self):
        sql = "CREATE TABLE IF NOT EXISTS sensors(date INT, temp REAL, humidity INT, carbon INT, acidity REAL, saline INT, level INT)"
        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql)
        conn.commit()
        conn.close()

    #delete table sensors
    def drop(self):
        sql = "DROP TABLE sensors"
        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql)
        conn.commit()
        conn.close()

    #insert test row into sensors table
    def testDataInsert(self):
        temp = random.randrange(-10, 30, 1)
        hum = random.randrange(0, 100, 1)
        carb = random.randrange(0, 1000, 10)
        acid = random.randrange(1, 15, 1)
        saline = random.randrange(0, 1000, 15)
        lvl = random.randint(0, 1)

        self.insertSensors(temp, hum, carb, acid, saline, lvl)

    #insert a row into sensors
    def insertSensors(self, temp='NULL', humidity='NULL', carbon='NULL', acidity='NULL', saline='NULL', level='NULL'):
        date = datetime.timestamp(datetime.now()) # FLOAT
        date = int(date) # INTEGER

        # print(date, temp, humidity, carbon, acidity, saline, level)

        sql = "INSERT INTO sensors(date, temp, humidity, carbon, acidity, saline, level) values(?, ?, ?, ?, ?, ?, ?)"
        val = (date, temp, humidity, carbon, acidity, saline, level)

        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql, val)
        conn.commit()
        conn.close()

    #count rows in sensors table
    def countSensors(self):

        sql = "SELECT COUNT(*) FROM sensors"

        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql)
        rows = curs.fetchall()
        conn.close()
        return rows[0][0]


    #select dsensors data of [fromTime; toTime] period
    def selectSensors(self, fromTime = None, toTime = None, limit = None):

        sql = "SELECT * FROM sensors"
        if fromTime:
            sql = sql + " WHERE date>=" + str(int(fromTime))
            if toTime:
                sql = sql + " AND date<=" + str(int(toTime))

        if limit:
            sql = sql + " LIMIT " + str(int(limit)) 


        # print(sql)

        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql)
        rows = curs.fetchall()
        conn.close()
        return rows

if __name__=="__main__":

    sq = Sqlite('./database/sensorsData.db')

    sq.create()
    sq.createActivity()

    #tests begin
    print('-----activity-----')
    sq.testActivity()
    for row in sq.selectActivity():
        print(row)
    print('-----sensors-----')
    sq.testDataInsert()
    print('total rows: '+str(sq.countSensors()))
    now = datetime.timestamp(datetime.now())
    print('----------------')
    for row in sq.selectSensors():
        print(row)
    print('----------------')
    for row in sq.selectSensors(now-3600*4):
        print(row)
    print('----------------')
    for row in sq.selectSensors(now-3600*6):
        print(row)
    print('----------------')
    for row in sq.selectSensors(now-3600*10, now):
        print(row)
    print('----------------')
    #tests end
