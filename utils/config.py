# -- Modules -- #

# Web App
from flask import Flask, render_template, request
import signal
import requests
from selectolax.parser import HTMLParser

# Main
import os, sys, shutil, subprocess, json, pathlib, threading, pyperclip, ctypes
from time import sleep
from datetime import datetime

# Capture
import webbrowser, pygetwindow

# Download
import m3u8
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Subtitles
import urllib.request, zipfile, srt, re

# Styling
import colorama
from termcolor import colored
# ================================================== #

# Initilizations
ROOT = os.path.dirname(os.path.dirname(__file__))
os.chdir(ROOT)
colorama.init()
# -------------------------------------------------- #

# Settings
settings_file_path = os.path.join(ROOT, "setup", "settings.json")

if (os.path.isfile(settings_file_path)):
    with open(settings_file_path) as settings_file:
        settings = json.load(settings_file)
        
        QUALITY = settings["QUALITY"]
        MOVIES_DIR = settings["MOVIES_DIR"]
        TVSHOWS_DIR = settings["TVSHOWS_DIR"]
        SUB_LANGUAGE = settings["SUB_LANGUAGE"]
else:
    raise Exception(" `settings.json` can't be found | run `setup.py` to setup settings")
# -------------------------------------------------- #

# -- CONSTANTS -- #

# Basic
BASE_URL = "https://solarmovie.pe"
APP = "app"
WEB_APP = "webApp"

# Paths
FIDDLER_PATH = os.path.join(ROOT, APP, "fiddler")
FIDDLER_TMP_REQUESTS = os.path.join(FIDDLER_PATH, "requests")
STAGE_FILE = os.path.join(ROOT, APP, "staged.json")

# Downloader
TIMEOUT = 3
MAX_TRIES = 3
MAX_EXT_TRIES = 2
SERVER = 1
ALL_EXT = ["jpg", "html", "js", "css", "png", "webp", "txt", "ico"]

# APIs
MOVIES_API = f"{BASE_URL}/ajax/movie/episodes/"
SEASONS_API = f"{BASE_URL}/ajax/v2/tv/seasons/"
EPISODES_API = f"{BASE_URL}/ajax/v2/season/episodes/"
EPISODES_WATCH_API = f"{BASE_URL}/ajax/v2/episode/servers/"

# Subtitles [Movies]
SUBTITLE_MOVIE_SEARCH = "https://www.opensubtitles.org/libs/suggest.php?format=json3&SubLanguageID=null"
SUBTITLE_SEARCH = f"https://www.opensubtitles.org/en/search/sublanguageid-{SUB_LANGUAGE}"

SUB_WEIGHT = 500
SUBTITLE_RANKS = {
    "trusted": SUB_WEIGHT,
    "silver member": SUB_WEIGHT,
    "gold member": 2*SUB_WEIGHT,
    "platinum member": 3*SUB_WEIGHT,
    "vip lifetime member": 5*SUB_WEIGHT
}
CURRENT_YEAR = datetime.now().year + 1

SHIT_SUB_WORDS = ["opensubtitles", "open-subtitles", "url%", "osdb", "translated", "ترجمة", "التوقيت"]
SUB_FILTER_PATTERN = "|".join(SHIT_SUB_WORDS)

ENCODERS = ["UTF-8", "Windows-1256"]
MAIN_ENCODER = "UTF-8"

# Subtitles [TV Shows]
SUBSCENE_URL = "https://subscene.com/"

# Functions constants
BROWSER = "Google Chrome"
START_PYTHON = ["start", "cmd", "/c", "python"]
SHIT_CHARS = ["?", "\\", "/", "|", "\"", ":", "*", "<", ">"]
LPAD = 100
# -------------------------------------------------- #