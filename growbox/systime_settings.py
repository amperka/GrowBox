import subprocess


def set_systime(date_time):
    command = ["sudo", "date", "--set=" + date_time]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        raise
