#!/usr/bin/python3

import subprocess
import sys
import os
import json
import datetime
import requests
import logging

from waitress import serve
from io import BytesIO

from flask import Flask, flash, url_for, redirect, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from manager import *

sys.path.append("../")

# from utils import send_to_display
from config import config

# app config
TEMPUS_FOLDER = config["TEMPUS_FOLDER"]
UPLOAD_FOLDER = config["UPLOAD_FOLDER"]
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "webp"}

manage_store = TEMPUS_FOLDER + "/output/managestore.json"
logger = logging.getLogger('tempusdash')

app = Flask(__name__)
app.secret_key = 'tempus'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
	if "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS:
		return True
	else:
		return False

def allowed_url(url):
	if any([url.endswith(e) for e in ALLOWED_EXTENSIONS]):
		try:
			response = requests.head(url, allow_redirects=True, timeout=10)
			response.raise_for_status()

			content_type = response.headers.get('Content-Type', '')
			if content_type.startswith('image/'):
				return True
			else:
				print("URL provided is not a valid image")
				return False
		except requests.exceptions.RequestException as e:
			print(f"Error checking URL {url}: {e}")
			return False
	else:
		print("URL provided is not a valid image")
		return False

def show_dash_status(status):
	now = datetime.datetime.now()

	manage_out = {
			"timestamp": now.timestamp(),
			"last_run": now.strftime("%B %d, %Y @ %H:%M"),
			"name": status
	}

	with open(manage_store, "w") as storefile:
		json.dump(manage_out, storefile, indent=4)

def handle_logger(message, success=True, code=200):
	if success:
		logger.info(message)
		return jsonify({'message': message, 'code': code})
	else:
		logger.info(message)
		return jsonify({'error': message, 'code': code})


@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
		# define dashboard buttons
		button_list = [
				{"id": "dashboard", "text": "Start Dashboard", "icon": "layout-dashboard.svg", "route":""},
				{"id": "photo", "text": "Display Image", "icon": "image.svg", "route":"/image-display"},
				{"id": "photolink", "text": "Display Image from URL", "icon": "square-arrow-up-right.svg", "route":""},
				{"id":"yearprogress", "text": "Year Progress", "icon": "calendar-1.svg", "route": "/progress-display"},
				{"id": "clear", "text": "Clear Dashboard", "icon": "brush-cleaning.svg", "route":"/clear"},
				{"id": "pause", "text": "Pause Dashboard", "icon": "circle-pause.svg", "route":"/dashstop"}
		]

		# get currently running utility
		with open(manage_store, "r") as storefile:
			storedict = json.load(storefile)

		# show list of uploaded images
		imagelist = os.listdir(app.config["UPLOAD_FOLDER"])

		return render_template('index.html', buttons=button_list, status=storedict, imagelist=imagelist)

def manage_screen(operation, fp=None):
	"""Run Waveshare display functions in isolated subprocess"""
	try:
		# Force cleanup any existing GPIO claims before starting
		subprocess.run(['python3', '-c', 'import gpiozero; gpiozero.Device.pin_factory.reset() if gpiozero.Device.pin_factory else None'],
									cwd=TEMPUS_FOLDER, timeout=5)

		# Run the actual operation
		if operation == 'dashboard':
			result = subprocess.run(['python3', 'main.py'],
									cwd=TEMPUS_FOLDER,
									capture_output=True, text=True, timeout=60)
		elif operation == 'photo':
			result = subprocess.run(['python3', 'photodisplay.py'],
									cwd=TEMPUS_FOLDER,
									capture_output=True, text=True, timeout=30)
		elif operation == 'clear':
			result = subprocess.run(['python3', 'clear.py'],
									cwd=TEMPUS_FOLDER,
									capture_output=True, text=True, timeout=30)
		elif operation == 'imagedisplay':
			the_cmd = f'import utils; utils.send_to_display("{fp}")'
			# print(photo_cmd)
			result = subprocess.run(['python3', '-c', the_cmd],
									cwd=TEMPUS_FOLDER,
									capture_output=True, text=True, timeout=30)

		elif operation == 'imageurl':
			the_cmd = f'import utils; utils.imageurl_to_display("{fp}")'
			# print(photo_cmd)
			result = subprocess.run(['python3', '-c', the_cmd],
									cwd=TEMPUS_FOLDER,
									capture_output=True, text=True, timeout=30)

		elif operation == 'yearprogress':
			result = subprocess.run(['python3', 'yearprogress.py'],
									cwd=TEMPUS_FOLDER,
									capture_output=True, text=True, timeout=60)

		return result.returncode == 0, result.stdout, result.stderr
	except subprocess.TimeoutExpired:
		return False, "", "Operation timed out"
	except Exception as e:
		return False, "", str(e)


# start dashboard route
@app.route('/dashstart', methods=['POST'])
def dashstart():
		if request.method == 'POST':
				data = request.form
				timer = data["input_data"]

				print(timer)

				hasjob = set_tempus_job(timer)

				if hasjob:
						success, stdout, stderr = manage_screen('dashboard')

						if success:
								result = f"Dashboard started successfully. Refresh time interval is {timer} minutes."
								return handle_logger(result, True, 200)
						else:
								errormsg = f'Dashboard not started: {stderr}'
								return handle_logger(errormsg, False, 400)
				else:
						errormsg = 'Dashboard not started'
						return handle_logger(errormsg, False, 400)
		else:
				errormsg = 'Invalid request from manager'
				return handle_logger(errormsg, False, 400)

# serve images from upload folder
@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
	return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# photo display page route
@app.route("/imagedisplay")
@app.route("/image-display")
def displayer():
	# show list of uploaded image
	images = sorted(os.listdir(app.config["UPLOAD_FOLDER"]))
	return render_template("display-image.html", images=images)

# upload photo route
@app.route("/upload", methods=['POST'])
def upload():
	if "file" not in request.files:
		flash('No file part', 'error')
		return redirect(url_for("displayer"))

	file = request.files["file"]

	if file.filename == "":
		flash('No file selected', 'error')
		return redirect(url_for("displayer"))

	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
		file.save(filepath)
		flash('Image uploaded successfully', 'success')
		return redirect(url_for("displayer"))

	flash('File type not allowed', 'error')
	return redirect(url_for("displayer"))

# display uploaded image route
@app.route('/showphoto/<filename>', methods=['POST'])
def showphoto(filename):
	stopped = clear_tempus_jobs()

	if not stopped:
		return handle_logger('Photo display failed', False, 400)

	try:
		filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
		success, stdout, stderr = manage_screen('imagedisplay', filepath)

		if success:
			result = "Switched to photo display mode"
			print(result)
			show_dash_status("Photo Display")
			return handle_logger(result)
		else:
			errormsg = f'Photo display failed: {stderr}'
			return handle_logger(errormsg, False, 400)
	except Exception as e:
		errormsg = f'Error displaying image: {e}'
		return handle_logger(errormsg, False, 400)

# display photo via url route
@app.route('/display-url', methods=['POST'])
def showimageurl():
	stopped = clear_tempus_jobs()
	if not stopped:
		errormsg = 'URL photo display failed'
		return handle_logger(errormsg, False, 400)

	try:
		url = request.form.get('input_data')
		if not url:
			errormsg = 'URL photo display failed'
			return handle_logger(errormsg, False, 400)

		if not allowed_url(url):
			errormsg = 'No valid URL provided'
			return handle_logger(errormsg, False, 400)

		success, stdout, stderr = manage_screen('imageurl', url)

		if success:
			result = "Switched to URL photo display mode"
			print(result)
			show_dash_status("Photo Display from URL")
			return handle_logger(result)
		else:
			errormsg = f'URL photo display failed: {stderr}'
			return handle_logger(errormsg, False, 400)
	except Exception as e:
		errormsg = f'Error displaying image from URL: {e}'
		return handle_logger(errormsg, False, 400)

# display photo route
@app.route('/showimage', methods=['POST'])
def showimage():
		stopped = clear_tempus_jobs()

		if stopped:
				success, stdout, stderr = manage_screen('photo')

				if success:
						result = "Switched to photo display mode"
						print(result)
						return handle_logger(result)
				else:
						errormsg = f'Photo display failed: {stderr}'
						return handle_logger(errormsg, False, 400)
		else:
			errormsg = 'Photo display failed'
			return handle_logger(errormsg, False, 400)

# year progress manager page route
@app.route("/progressdisplay")
@app.route("/progress-display")
def progress_display():
	return render_template("display-progress.html")

# year progress display route
@app.route('/yearprogress', methods=['POST'])
def showprogress():
	if request.method == 'POST':
		data = request.form
		action = data["action"]

		hasjob = False
		hour = -1

		if action == "flash":
			hasjob = True
		elif action == "update":
			hour = int(data["hour"])
			hasjob = set_progress_job(hour)

		if hasjob:
			success, stdout, stderr = manage_screen('yearprogress')

			if success:
				if hour > 0:
					result = f"Year progress displayed. Progress will display every day at {hour} o'clock."
				else:
					result = "Year progress displayed"
				flash(result, "success")
				return redirect(url_for("progress_display"))

			else:
				errormsg = f'Year progress not displayed: {stderr}'
				flash(errormsg, "error")
				return redirect(url_for("progress_display"))
		else:
			errormsg = "Year Progress not displayed"
			flash(errormsg, "error")
			return redirect(url_for("progress_display"))
	else:
		errormsg = 'Invalid request from manager'
		flash(errormsg, "error")
		return redirect(url_for("progress_display"))

# clear screen route
@app.route('/clear', methods=['POST'])
def cleardash():
		success, stdout, stderr = manage_screen('clear')

		if success:
				result = "Dashboard Cleared Successfully"
				print(result)
				show_dash_status("Dashboard Paused")
				return handle_logger(result)
		else:
				errormsg = f'Clear failed: {stderr}'
				return handle_logger(errormsg, False, 400)

# stop dashboard cron job route
@app.route('/dashstop', methods=['POST'])
def dashstop():
		stopped = clear_tempus_jobs()

		if stopped:
				result = "Dashboard Paused Successfully"
				print(result)
				show_dash_status("Dashboard Paused")
				return handle_logger(result)
		else:
				return handle_logger('Dashboard not paused', False, 400)

if __name__ == "__main__":
	serve(app, host="0.0.0.0", port=5555, threads=1)
