#!/usr/bin/python3

import utils
import subprocess

from crontab import CronTab
from manage.manager import set_tempus_job

from config import config

TEMPUS_FOLDER = config["TEMPUS_FOLDER"]

def set_portal_job():
    command = "sleep 60 && cd ~/tempus-db/manage/ && python app.py"

    cron = CronTab(user=True)
    cron.remove_all(command=command)

    job = cron.new(command=command, comment="boot")
    job.every_reboot()
    cron.write()

    return len(cron) > 0

def clear_portal_job():
  command = "sleep 60 && cd ~/tempus-db/manage/ && python app.py"

  cron = CronTab(user=True)
  portal_jobs = cron.find_command(command)

  for job in portal_jobs:
    cron.remove(job)

  cron.write()

  portal_jobs = cron.find_command(command)
  jobcount = sum(1 for _ in portal_jobs)

  return jobcount == 0

if __name__ == "__main__":
  utils.cleanup_gpio()
  utils.clear_display()

  result = subprocess.run(['python3', 'main.py'],
                        cwd=TEMPUS_FOLDER,
                        capture_output=True, text=True, timeout=60)

  set_tempus_job()
