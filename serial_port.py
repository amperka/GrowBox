import serial
import time
import multiprocessing

class SerialProcess(multiprocessing.Process):

    def __init__(self, output_queue, input_queue, serial_port, baudrate=9600, timeout=1):
        multiprocessing.Process.__init__(self, target=self.run)
        self.output_queue = output_queue
        self.input_queue = input_queue
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout

    def open(self):
        self.sp = serial.Serial(self.serial_port, self.baudrate, timeout=self.timeout)

    def close(self):
        self.sp.close()

    def read_serial(self):
        return self.sp.readline().decode('utf-8')
    
    def write_serial(self, data):
        self.sp.write(data)

    def run(self):
        self.open()
        self.sp.flushInput()
        try:
            while True:
                if not self.input_queue.empty():
                    data = self.input_queue.get()
                    self.write_serial(data.encode())
                    print("Write data to serial " + data) #testing
                
                # look for incoming serial data
                while self.sp.inWaiting():
                    if not self.output_queue.full():
                        data = self.read_serial() #read data from serial port
                        self.output_queue.put(data) #put data in Queue
                        print(self.output_queue.qsize()) #testing
                    else:
                        self.sp.flushInput()
                #print('sleep') #testing   
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.close()
            print("Interrupt by user")

def get_data_from_serial(output_queue):
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
            temp, hum, ph, tds, co2 = get_data_from_serial(output_queue)
            print(temp, hum, ph, tds, co2)
