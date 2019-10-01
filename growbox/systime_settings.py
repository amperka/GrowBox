import os


def set_systime(date_time):
    os.system("sudo date --set='" + date_time + "'")
