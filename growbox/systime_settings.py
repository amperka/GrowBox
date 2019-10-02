import subprocess


def set_systime(date_time):
    command = ["sudo", "date", "--set=" + date_time]
    subprocess.run(command, check=True)
