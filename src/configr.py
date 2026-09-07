import pathlib
import tomllib

config_path = "/config.toml"
tempus_path = str(pathlib.Path(__file__).parent.absolute())

with open(tempus_path + config_path, "rb") as f:
    config = tomllib.load(f)

config["tempus_folder"] = tempus_path
config["upload_folder"] = tempus_path + config["photo_folder"]
