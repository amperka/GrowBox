import sqlite3

def getData():
    conn = sqlite3.connect("./Sensors_Database/sensorsData.db")
    curs = conn.cursor()

    for row in curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT 1"):
        time = str(row[0])
        temp = row[1]
        hum = row[2]
    conn.close()
    return time, temp, hum

def getHistData(numSamples):
    conn = sqlite3.connect("./Sensors_Database/sensorsData.db")
    curs = conn.cursor()
    curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT "+str(numSamples))
    data = curs.fetchall()
    dates = []
    temps = []
    hums = []
    for row in reversed(data):
        dates.append(row[0])
        temps.append(row[1])
        hums.append(row[2])
    return dates, temps, hums


if __name__ == "__main__":
    print("Last data log on database")
    time, temp, hum = getData()
    print("Time {0}, temp {1}, hum {2}".format(time, temp, hum))  
    print("10 temp data log")
    print((getHistData(10))[1])
    print("10 hum data log")
    print((getHistData(10))[2])
