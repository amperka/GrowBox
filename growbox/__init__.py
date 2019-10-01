import os
import signal
import sys
import logging

from flask import Flask
import threading

from growbox.database import get_db


def create_app():
    # Create own logger
    logger = create_logger()

    # Create Flask app
    TEMPLATE_DIR = os.path.abspath("./templates")
    STATIC_DIR = os.path.abspath("./static")
    app = Flask(
        __name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR
    )
    with app.app_context():
        # Create database
        db = get_db()
        # Import and register blueprint from views
        from growbox.views import main as main_blueprint

        app.register_blueprint(main_blueprint)

    # Create sensors and activity tables in database.
    db.create_sensors()
    db.create_activity()

    # Create Arduino thread.
    from growbox.arduino_thread import read_arduino, init_actuators_state

    thread = threading.Thread(target=read_arduino, args=(db,))
    thread.daemon = True

    def stop_ser_thread():
        from growbox.arduino_thread import input_queue

        if thread.is_alive():
            input_queue.put("Exit")
            thread.join()

    def sigint_handler(signum, frame):
        logger.info("Process was terminated by SIGINT")
        stop_ser_thread()
        logger.info("Exit application")
        sys.exit(1)

    def sigterm_handler(signum, frame):
        logger.info("Process was terminater by SIGTERM")
        stop_ser_thread()
        logger.info("Arduino thread successfully closed")

    # Set signal handlers for stopping app.
    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)
    # Set the initial state of actuators.
    init_actuators_state(db)

    return app, thread, logger


def create_logger():
    # Create own logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # Create logging file handler
    file_handler = logging.FileHandler("growbox.log")
    date_format = "%Y-%m-%d %H:%M:%S"
    message_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(message_format, date_format)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
