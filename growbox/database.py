from flask import g

from growbox.sqlite import Sqlite


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = Sqlite("./sensorsData.db")
    return db
