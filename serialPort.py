import serial
import time
import multiprocessing

class SerialProcess(multiprocessing.Process):

    def __init__(self, output_queue, serial_port, baudrate=9600, timeout=1):
        multiprocessing.Process.__init__(self, target=self.run)
        self.output_queue = output_queue
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout

    def open(self):
        self.sp = serial.Serial(self.serial_port, self.baudrate, timeout=self.timeout)

    def close(self):
        self.sp.close()

    def readSerial(self):
        return self.sp.readline().decode('utf-8')

    def run(self):
        self.open()
        try:
            while True:
                # look for incoming serial data
                if (self.sp.inWaiting() > 0):
                    data = self.readSerial()
                    # send it back
                    self.output_queue.put(data)
                    print(self.output_queue.qsize()) #testing
        except KeyboardInterrupt:
            self.close()
            print("Interrupt by user")

def getDataFromSerial(output_queue):
    data = output_queue.get()
    dataList = data.split()
    return tuple(dataList)


if __name__ == "__main__":
    temp, hum, ph, tds, co2 = (0, 0, 0, 0, 0)

    output_queue = multiprocessing.Queue()
    sp = SerialProcess(output_queue)
    sp.daemon = True
    sp.start()
    while(True):
        if not output_queue.empty():
            temp, hum, ph, tds, co2 = getDataFromSerial(output_queue)
            print(temp, hum, ph, tds, co2)
