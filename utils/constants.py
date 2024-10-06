# Modules
import os, sys, json
# ===================================================================== #

# check OS
if (sys.platform != "win32"):
    input("This app can ONLY run on Windows")
    exit()
# --------------------------------------------------------------------- #

# Initilizations
ROOT = os.path.dirname(os.path.dirname(__file__))
# --------------------------------------------------------------------- #

# Settings
settings_file_path = os.path.join(ROOT, "setup", "settings.json")

if (os.path.isfile(settings_file_path)):
    with open(settings_file_path) as settings_file:
        settings = json.load(settings_file)
        
        QUALITY = settings["QUALITY"]
        MOVIES_DIR = settings["MOVIES_DIR"]
        TVSHOWS_DIR = settings["TVSHOWS_DIR"]
        BROWSER = settings["BROWSER"]
else:
    raise Exception(" `settings.json` can't be found | run `setup.py` to setup settings")
# --------------------------------------------------------------------- #

# Basic
BASE_URL = "https://hdtoday.tv"
APP = "app"

# Paths
STAGE_FILE = os.path.join(ROOT, APP, "staged.json")

# Console
LINE_WIDTH = 120
# --------------------------------------------------------------------- #