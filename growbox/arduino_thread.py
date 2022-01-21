import subprocess
import queue
import json
from datetime import datetime
import threading
import logging
import time

from flask import Markup

from growbox import serial_port, systime_settings

# Сreate the input queue for actuators control.
input_queue = queue.Queue(1)
# Create mutex for sensors data.
lock = threading.Lock()

ARRAY_LEN = 600
circular_array = [0] * ARRAY_LEN
array_pivot = 0

sensors_dict = {"temp": 0, "ph": 0, "tds": 0, "co2": 0, "lvl": 0}

arduino_logger = logging.getLogger(__name__)


def read_arduino(db):
    arduino_path = auto_detect_serial()
    if arduino_path is not None:
        sp = serial_port.SerialPort(arduino_path)
    else:
        arduino_logger.error("Arduino not connected")
        return

    try:
        sp.open()
    except OSError as err:
        arduino_logger.error(err)
        return

    data = {"temp": 0, "carb": 0, "acid": 0, "salin": 0, "level": 0}
    empty_loop_count = 0
    reconnect_count = 0
    first_data_pack_flag = False
    while True:
        try:
            if not input_queue.empty():
                command_data = input_queue.get()
                if command_data == "Exit":
                    break
                sp.write_serial(command_data.encode())
                arduino_logger.debug("Write data to serial " + command_data)

            while sp.serial_available():
                empty_loop_count = 0
                data = json.loads(sp.read_serial())
                if not first_data_pack_flag:
                    reconnect_count = 0
                    current_time = datetime.utcfromtimestamp(data["time"])
                    systime_settings.set_systime(str(current_time))
                    first_data_pack_flag = True
            empty_loop_count += 1
            if empty_loop_count > 10:
                raise RuntimeError("Time is over")
        # Exception from set_systime
        except subprocess.CalledProcessError:
            sp.close()
            arduino_logger.error("Error setting the system time")
            return
        # Exception when faulty data from Arduino
        except json.JSONDecodeError as err:
            sp.close()
            arduino_logger.error(err)
            arduino_logger.error("Error in Arduino firmware")
            return
        except (RuntimeError, OSError):
            sp.close()
            arduino_logger.error("Serial port disconnect")
            arduino_logger.info("Try to reconnect")
            reconnect_count += 1
            if reconnect_count > 3:
                arduino_logger.info(
                    "Reconnection limit. Please restart your computer."
                )
                return
            time.sleep(10)
            arduino_path = auto_detect_serial()
            if arduino_path is not None:
                sp = serial_port.SerialPort(arduino_path)
            else:
                arduino_logger.error("Arduino not connected")
                return
            try:
                sp.open()
                empty_loop_count = 0
                arduino_logger.info("Connection succeful")
                init_actuators_state(db)
            except OSError as err:
                arduino_logger.error(err)
                return

        with lock:
            sensors_dict["temp"] = data["temp"]
            sensors_dict["ph"] = data["acid"]
            sensors_dict["tds"] = data["salin"]
            sensors_dict["co2"] = data["carb"]
            sensors_dict["lvl"] = data["level"]
            insert_data_into_db(
                db,
                sensors_dict["temp"],
                sensors_dict["ph"],
                sensors_dict["tds"],
                sensors_dict["co2"],
                sensors_dict["lvl"],
            )

        time.sleep(1)
    sp.close()
    arduino_logger.debug("Serial port thread successfully terminated")


def auto_detect_serial():
    import glob

    path = glob.glob("/dev/ttyACM*")
    if len(path) > 0:
        return path[0]
    else:
        return None


def insert_data_into_db(db, temp, ph, tds, co2, lvl):
    global array_pivot, circular_array

    circular_array[array_pivot] = (
        float(temp),
        float(ph),
        float(tds),
        float(co2),
    )
    array_pivot += 1
    if array_pivot == ARRAY_LEN:
        s = tuple([round(sum(x) / ARRAY_LEN, 2) for x in zip(*circular_array)])
        db.insert_sensors(
            temp=s[0], carbon=s[3], acidity=s[1], saline=s[2], level=lvl
        )
        array_pivot = 0


# Initial settings.
def init_actuators_state(db):
    row = db.select_activity()
    current_state = Markup(row[0][0])
    input_queue.put(current_state)
