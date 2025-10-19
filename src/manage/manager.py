from crontab import CronTab
import subprocess
import sys

def set_tempus_job(timer=10):
    command = "cd ~/tempus-db/ && python main.py"

    cron = CronTab(user=True)
    cron.remove_all(command=command)

    job = cron.new(command=command, comment="tempus")
    job.minute.every(timer)
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

def clear_display():
    """Clear display using subprocess to avoid GPIO conflicts"""
    try:
        result = subprocess.run([
            'python3', 'gpio_wrapper.py', 'clear'
        ], cwd='/home/tempus/tempus-db', capture_output=True, text=True, timeout=30)

        return result.returncode == 0
    except Exception:
        return False
