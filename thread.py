import time
from threading import Lock, Thread
lock = Lock()

def runThread(self, essentData):
    while True:
        time.sleep(2)
        essentData = essentData + 1
        print(essentData)