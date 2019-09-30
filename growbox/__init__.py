import os

from flask import Flask

from growbox import sqlite

TEMPLATE_DIR = os.path.abspath("./templates")
STATIC_DIR = os.path.abspath("./static")
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Create database for sensors and activities.
sql = sqlite.Sqlite("./sensorsData.db")
# Create sensors and activity tables in database.
sql.create_sensors()
sql.create_activity()

import growbox.server as gb
