import serial


class SerialPort:
    def __init__(self, serial_port, baudrate=9600, timeout=1):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout

    def open(self):
        try:
            self.sp = serial.Serial(self.serial_port, self.baudrate,
                                    timeout=self.timeout)
            self.sp.flushInput()
        except serial.SerialException:
            raise

    def close(self):
        self.sp.close()

    def read_serial(self):
        return self.sp.readline().decode('utf-8')

    def write_serial(self, data):
        self.sp.write(data)

    def serial_available(self):
        return self.sp.inWaiting()


if __name__ == "__main__":
    import sys
    import time

    sp = SerialPort("/dev/ttyACM0")

    try:
        sp.open()
    except OSError as err:
        print(err)
        sys.exit(1)

    try:
        while True:
            while sp.serial_available():
                data = sp.read_serial()
                print(data)
            time.sleep(1)
    except KeyboardInterrupt:
        sp.close()
