#!/usr/bin/python3

import subprocess
import sys
import os
import json
import datetime
import requests
import logging
import csv

from waitress import serve
from io import BytesIO

from flask import Flask, flash, url_for, redirect, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from manager import *

sys.path.append("../")

from utils import update_history
from lib.datastore import DataStore
from configr import config

# app config
TEMPUS_FOLDER = config["tempus_folder"]
UPLOAD_FOLDER = config["upload_folder"]
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "webp"}

logger = logging.getLogger('tempusdash')

storepath = TEMPUS_FOLDER + "/output/datastore.json"

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

def show_dash_status(status, storepath=storepath):
    now = datetime.datetime.now()

    timestamp = now.timestamp()
    current_app = status


    ds = DataStore(storepath, flag='c')
    ds["timestamp"] = timestamp
    ds["current_app"] = current_app
    ds.close()

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
            {"id": "wordclock", "text": "Word Clock", "icon": "clock.svg", "route": "/wordclock"},
            {"id":"qrcode", "text": "Display QR Code", "icon": "qr-code.svg", "route": "/qrcode-display"},
            {"id":"textdisplay", "text": "Display Message", "icon": "text-initial.svg", "route": "/textdisplay"},
            {"id": "clear", "text": "Clear Dashboard", "icon": "brush-cleaning.svg", "route":"/clear"},
            {"id": "pause", "text": "Pause Dashboard", "icon": "circle-pause.svg", "route":"/dashstop"},
            {"id": "history", "text": "View History", "icon": "chart-bar-stacked.svg", "route": "/history"},
    ]

    # get currently running utility
    ds = DataStore(storepath, flag='r')
    status = {
        "timestamp": ds["timestamp"],
        "last_run": datetime.datetime.fromtimestamp(ds["timestamp"]).strftime("%Y-%m-%d @ %H:%M"),
        "current_app": ds["current_app"]
    }
    ds.close()

    # show list of uploaded images
    imagelist = os.listdir(app.config["UPLOAD_FOLDER"])

    return render_template('index.html', buttons=button_list, status=status, imagelist=imagelist)


# start dashboard route
@app.route('/dashstart', methods=['POST'])
def dashstart():
    stopped = clear_tempus_jobs()
    if not stopped:
        errormsg = 'Weather dashboard display failed'
        return handle_logger(errormsg, False, 400)

    if request.method == 'POST':
        data = request.form
        timer = data["input_data"]

        print(timer)

        hasjob = set_tempus_job(timer)

        if hasjob:
            success, stdout, stderr = manage_display('dashboard')

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

# Route to display history
@app.route("/history")
def history():
    if not os.path.exists(f"{TEMPUS_FOLDER}/output/history.csv"):
        return render_template("history.html", history=[])

    with open(f"{TEMPUS_FOLDER}/output/history.csv", 'r') as f:
        history = csv.DictReader(f)
        history = list(history)
    return render_template("history.html", history=history)

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
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        success, stdout, stderr = manage_display('imagedisplay', path=filepath)

        if success:
            result = "Switched to photo display mode"
            print(result)
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

        success, stdout, stderr = manage_display('imageurl', url=url)

        if success:
            result = "Switched to URL photo display mode"
            print(result)
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
        success, stdout, stderr = manage_display('photo')

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
            success, stdout, stderr = manage_display('yearprogress')

            if success:
                if hour >= 0:
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

# QR code manager page route
@app.route("/qrcodedisplay")
@app.route("/qrcode-display")
def qrcode_display():
    return render_template("display-qrcode.html")

# QR code display route
@app.route('/qrcode', methods=['POST'])
def qrcode():
    stopped = clear_tempus_jobs()
    if not stopped:
        errormsg = 'QR code display failed'
        flash(errormsg, "error")
        return redirect(url_for("qrcode_display"))

    if request.method == 'POST':
        data = request.form
        title = data.get('qrcode-title')
        texturl = data.get('qrcode-data')
        description = data.get('description', None)
        showdata = data.get('show-data') == "on"

        # print(title, texturl, description, showdata)

        success, stdout, stderr = manage_display('qrcode', title=title, data=texturl, description=description, showdata=showdata)

        if success:
            result = "QR code displayed successfully."
            flash(result, "success")
            return redirect(url_for("qrcode_display"))
        else:
            errormsg = f'QR code display failed: {stderr}'
            flash(errormsg, "error")
            return redirect(url_for("qrcode_display"))
    else:
        errormsg = 'QR code display failed.'
        flash(errormsg, "error")
        return redirect(url_for("qrcode_display"))

# Message display page route
@app.route("/textdisplay")
@app.route("/text-display")
def text_display():
    return render_template("display-message.html")

# Send message to e-paper display
@app.route("/messenger", methods=['POST'])
def send_message():
    stopped = clear_tempus_jobs()
    if not stopped:
        errormsg = 'Message display failed.'
        flash(errormsg, "error")
        return redirect(url_for("text_display"))

    if request.method == 'POST':
        data = request.form
        message = data.get('message')
        html = f"""{data.get('md-text')}"""
        fontsize = float(data.get('fontsize')) * 16

        print(message, html, fontsize)

        success, stdout, stderr = manage_display('message', html=html, font_size=fontsize)

        if success:
            result = "Message displayed successfully."
            flash(result, "success")
            return redirect(url_for("text_display"))
        else:
            errormsg = f'Message display failed: {stderr}'
            flash(errormsg, "error")
            return redirect(url_for("text_display"))
    else:
        errormsg = 'Message display failed.'
        flash(errormsg, "error")
        return redirect(url_for("text_display"))


# Word clock display

@app.route('/wordclock', methods=['POST'])
def wordclock():
    stopped = clear_tempus_jobs()
    if not stopped:
        errormsg = 'QR code display failed'
        return handle_logger(errormsg, False, 400)

    hasjob = set_wordclock_job()

    if hasjob:
        success, stdout, stderr = manage_display('wordclock')
        if success:
            result = "Word clock display mode activated."
            return handle_logger(result, True, 200)
        else:
            errormsg = f'Word clock display failed: {stderr}'
            return handle_logger(errormsg, False, 400)
    else:
        errormsg = 'Word clock display failed.'
        return handle_logger(errormsg, False, 400)


# clear screen route
@app.route('/clear', methods=['POST'])
def cleardash():
        success, stdout, stderr = manage_display('clear')

        if success:
                result = "Dashboard Cleared Successfully"
                print(result)
                show_dash_status("dashclear")
                update_history('clear', datetime.datetime.now().timestamp())
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
                show_dash_status("dashpaused")
                update_history('dashstop', datetime.datetime.now().timestamp())
                return handle_logger(result)
        else:
                return handle_logger('Dashboard not paused', False, 400)

if __name__ == "__main__":
    port = 5555
    print(f"Server starting on port {port}...")
    serve(app, host="0.0.0.0", port=port, threads=1)
