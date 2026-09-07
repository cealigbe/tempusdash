from crontab import CronTab
import subprocess
import sys
import os

sys.path.append("../")

from configr import config

TEMPUS_FOLDER = config["tempus_folder"]

def set_tempus_job(timer=10):
    command = f"cd {TEMPUS_FOLDER} && python3 tempus.py"

    cron = CronTab(user=True)
    cron.remove_all(command=command)

    job = cron.new(command=command, comment="tempus")
    job.minute.every(timer)
    cron.write()

    return len(cron) > 0

def set_progress_job(hour=8):
  command = f"cd {TEMPUS_FOLDER} && python3 yrprog.py"

  cron = CronTab(user=True)
  cron.remove_all(command=command)

  job = cron.new(command=command, comment="tempus")
  job.setall(f"4 {hour} * * *")
  cron.write()

  return len(cron) > 0

def set_wordclock_job():
    command = f"cd {TEMPUS_FOLDER} && python3 wordclock.py"

    cron = CronTab(user=True)
    cron.remove_all(command=command)

    job = cron.new(command=command, comment="tempus")
    job.minute.every(1)
    cron.write()

    return len(cron) > 0

def clear_jobs():
    cron = CronTab(user=True)
    cron.remove_all()
    cron.write()

    return len(cron) == 0

def clear_tempus_jobs():
    cron = CronTab(user=True)
    tempus_jobs = cron.find_comment('tempus')

    for job in tempus_jobs:
        cron.remove(job)

    cron.write()

    tempus_jobs = cron.find_comment('tempus')
    jobcount = sum(1 for _ in tempus_jobs)

    return jobcount == 0

def disable_tempus_jobs():
    cron = CronTab(user=True)
    for job in cron:
        if job.comment == "tempus":
            job.enable(False)

    return "disabled"

def enable_tempus_jobs():
    cron = CronTab(user=True)
    for job in cron:
        if job.comment == "tempus":
            job.enable()

    return "enabled"

def list_tempus_jobs():
  cron = CronTab(user=True)

  joblist = []

  for job in cron:
    if job.comment == "tempus":
      joblist.append((str(job.minutes), job.command))

  return joblist

def manage_display(operation: str, **kwargs):
    "Run a display operation using subprocess to avoid GPIO conflicts"

    operations = {
        "dashboard": {
            "command": ["tempus.py"],
            "timeout": 60
        },
        "photo": {
            "command": ["photodisplay.py"],
            "timeout": 30
        },
        "clear": {
            "command": ["clear.py"],
            "timeout": 30
        },
        "imagedisplay": {
            "command": ["-c", f"import imagedisplay; imagedisplay.display_image('{kwargs.get('path', '')}')"],
            "timeout": 30
        },
        "imageurl": {
            "command": ["-c", f"import imagedisplay; imagedisplay.display_imageurl('{kwargs.get('url', '')}')"],
            "timeout": 30
        },
        "yearprogress": {
            "command": ["yrprog.py"],
            "timeout": 60
        },
        "qrcode": {
            "command": ["-c", f"import qrdisplay; qrdisplay.display_qr('{kwargs.get('title', '')}', '{kwargs.get('data', '')}', '{kwargs.get('description', '')}', showdata={kwargs.get('showdata', '')})"],
            "timeout": 40
        },
        "message": {
            "command": ["-c", f"import textdisplay; textdisplay.display_message('''{kwargs.get('html', '')}''', {kwargs.get('font_size', 16)})"],
            "timeout": 40
        },
        "wordclock": {
            "command": ["wordclock.py"],
            "timeout": 60
        }
    }

    if operation not in operations:
        raise ValueError(f"Invalid operation: {operation}")

    command = ["python3"] + operations[operation]["command"]
    timeout = operations[operation]["timeout"]

    try:
        result = subprocess.run(command, cwd=TEMPUS_FOLDER, capture_output=True, text=True, timeout=timeout)

        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Operation timed out"
    except Exception as e:
        return False, "", str(e)


def clear_display():
    """Clear display using subprocess to avoid GPIO conflicts"""
    try:
        result = subprocess.run([
            'python3', 'clear.py'
        ], cwd=TEMPUS_FOLDER, capture_output=True, text=True, timeout=30)

        return result.returncode == 0
    except Exception:
        return False
