#!/usr/bin/python3
import sqlite3
from datetime import datetime
import random


class Sqlite:

    def __init__(self, db_filename):
        self.dbname = db_filename

    # Create table activity
    def create_activity(self):
        sql = ("CREATE TABLE IF NOT EXISTS activity(curstate TEXT, lamp INT "
               "DEFAULT 1, fan INT DEFAULT 1, compressor INT DEFAULT 1)")
        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql)
        conn.commit()
        conn.close()

        if len(self.select_activity()) == 0:
            conn = sqlite3.connect(self.dbname)
            curs = conn.cursor()
            curstate = str({'compressor': 0, 'fan': [0, 1], 'lamp': [0, 18]})
            sql = "INSERT INTO activity(curstate) values(?)"
            val = (curstate,)
            curs.execute(sql, val)
            conn.commit()
            conn.close()

    # Test activity
    def test_activity(self):

        curstate = str({'compressor': 0, 'fan': [0, 1], 'lamp': [0, 18]})
        lamp = random.randrange(0, 100, 1)
        fan = random.randrange(0, 100, 1)
        compressor = random.randrange(0, 100, 1)

        print(curstate, lamp, fan, compressor)

        self.update_activity(curstate, lamp, fan, compressor)

    # Update a row of activity
    def update_activity(
            self, curstate={}, lampMode=1, fanMode=1, compressorMode=1):

        lamp = str(int(lampMode))
        fan = str(int(fanMode))
        compressor = str(int(compressorMode))

        sql = ("UPDATE activity SET curstate=?, "
               "lamp=?, fan=?, compressor=? WHERE 1=1")
        val = (curstate, lamp, fan, compressor)

        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql, val)
        conn.commit()
        conn.close()

    # Select from activity
    def select_activity(self):
        sql = "SELECT * FROM activity"

        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql)
        rows = curs.fetchall()
        conn.close()
        return rows

    # Create table sensors
    def create_sensors(self):
        sql = ("CREATE TABLE IF NOT EXISTS sensors(date INT, temp REAL, "
               "carbon INT, acidity REAL, saline INT, level INT)")
        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql)
        conn.commit()
        conn.close()

    # Delete table sensors
    def drop(self):
        sql = "DROP TABLE sensors"
        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql)
        conn.commit()
        conn.close()

    # Insert test row into sensors table
    def test_data_insert(self):
        temp = random.randrange(20, 25, 1)
        carb = random.randrange(400, 500, 10)
        acid = random.randrange(1, 14, 1)
        saline = random.randrange(0, 1000, 15)
        lvl = random.randint(0, 1)

        self.insert_sensors(temp, carb, acid, saline, lvl)

    # Insert a row into sensors
    def insert_sensors(
            self, temp='NULL', carbon='NULL',
            acidity='NULL', saline='NULL', level='NULL'):
        date = datetime.timestamp(datetime.now())
        date = int(date)

        sql = ("INSERT INTO sensors(date, temp, carbon, acidity, "
               "saline, level) values(?, ?, ?, ?, ?, ?)")
        val = (date, temp, carbon, acidity, saline, level)

        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql, val)
        conn.commit()
        conn.close()

    # Count rows in sensors table
    def count_sensors(self):

        sql = "SELECT COUNT(*) FROM sensors"

        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql)
        rows = curs.fetchall()
        conn.close()
        return rows[0][0]

    # Select sensors data of [from_time; to_time] period
    def select_sensors(
            self, param=[], from_time=None, to_time=None, limit=None):

        select = "*"
        if type(param) is str:
            select = "date," + param
        else:
            if len(param) > 0:
                select = "date," + ",".join(param)

        sql = "SELECT " + select + " FROM sensors"
        if from_time:
            sql = sql + " WHERE date>=" + str(int(from_time))
            if to_time:
                sql = sql + " AND date<=" + str(int(to_time))

        sql = sql + " ORDER BY date DESC"

        if limit:
            sql = sql + " LIMIT " + str(int(limit))

        sql = "SELECT * from (" + sql + ") ORDER BY date ASC"

        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        curs.execute(sql)
        rows = curs.fetchall()
        conn.close()
        return rows


if __name__ == "__main__":

    sq = Sqlite("./testData.db")

    sq.create_sensors()
    sq.create_activity()

    # Tests begin
    print('-----activity-----')
    sq.test_activity()
    for row in sq.select_activity():
        print(row)
    print('Activity length:')
    print(len(sq.select_activity()))
    print('-----sensors-----')
    for i in range(10):
        sq.test_data_insert()
    print('total rows: '+str(sq.count_sensors()))
    now = datetime.timestamp(datetime.now())
    print("Time now", now)
    print('----------------')
    for row in sq.select_sensors():
        print(row)
    print('----------------')
    # Tests end
