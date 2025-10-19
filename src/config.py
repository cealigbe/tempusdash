import pathlib

tempus_path = str(pathlib.Path(__file__).parent.absolute())

# basic configuration settings (adjust as needed)
config = {
		"location": "[[your city]]",
		"apikey": "[[your api key]]",
		"imgWidth": 800,
		"imgHeight": 480,
		"rotateAngle": 0,
		"dashboard_image_path": "output/tempusdash.png",
		"wordclock_image_path": "output/wordclock.png",
		"weather_store": "output/weatherstore.json",
		"error_store": "output/errorstore.json",
		"manage_store": "output/managestore.json",
		"photo_path": "photo-display/photo.png",
		"error_photo": "photo-display/error.png",

		"TEMPUS_FOLDER": tempus_path,
		"UPLOAD_FOLDER": tempus_path + "/photo-display"
}
