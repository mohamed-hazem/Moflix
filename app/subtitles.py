# Utils
from root_config import *
from utils import *

# Modules
import requests
import webbrowser
import zipfile
from glob import glob
import traceback

from app.capturer import Capturer
# ===================================================================== #

class MoviesSubtitles:
    MOVIE_SEARCH_API = "https://api.subsource.net/api/searchMovie"
    SUBTITLE_PAGE = "https://subsource.net/subtitles/{url}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    def __init__(self, title: str):
        self.title = title
        self.path = os.path.join(MOVIES_DIR, title)
        self.sub_file = os.path.join(self.path, f"{title}.srt")
        self.zip_file = os.path.join(self.path, f"{title}.zip")
    # ---------------------------------------------- #

    def open_subtitles_search(self):
        response = requests.post(self.MOVIE_SEARCH_API, data={"query": self.title})
        if (response.status_code == 200):
            url = response.json()["found"][0]["linkName"]
            webbrowser.open(self.SUBTITLE_PAGE.format(url=url))
        else:
            raise Exception(f"Error while searching a subtitle for {self.title}")
    # ---------------------------------------------- #

    def get_subtitle_url(self) -> str:
        while True:
            sub_url = input("Subtitle URL: ").strip()
            if (sub_url.startswith("https://api.subsource.net/api/downloadSub/")):
                return sub_url
            else:
                cprint(" Invalid URL", color="red")
    # ---------------------------------------------- #

    def download_subtitle(self, sub_url: str):
        # download subtitle ".zip" file
        response = requests.get(sub_url, headers=self.headers)
        if (response.status_code == 200):
            with open(self.zip_file, "wb") as f:
                f.write(response.content)
        else:
            raise Exception("Failed to download subtitle file!")

        # extract subtitle files
        with zipfile.ZipFile(self.zip_file, "r") as zip_ref:
            zip_ref.extractall(self.path)

            for file in zip_ref.infolist():
                file = os.path.join(self.path, file.filename)
                if (file.endswith("srt")):
                    os.rename(file, self.sub_file)
                else:
                    os.remove(file)
        
        # remove ".zip" file
        os.remove(self.zip_file)
# --------------------------------------------------------------------- #

class TvShowsSubtitles:
    TV_SHOWS_SEARCH_API = "https://api.subsource.net/api/searchMovie"
    SUBTITLE_PAGE = "https://subsource.net/subtitles/{url}/season-{season}"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    def __init__(self, url: str, title: str, season: int) -> None:
        self.url = url
        self.title = title
        self.season = season
        self.vid = url.split("-")[-1]

        self.path = os.path.join(TVSHOWS_DIR, title, f"Season {season}")
        self.subs_path = os.path.join(self.path, "subs")
        self.zip_file = os.path.join(self.path, f"{title}.zip")
    # ---------------------------------------------- #

    def get_episodes(self):
        capturer = Capturer(self.url, self.vid, "TV", self.title, self.season, episodes=(None, None))
        capturer.get_watch_urls()
        self.episodes = list(capturer.watch_urls.keys())
    # ---------------------------------------------- #

    def open_subtitles_search(self):
        response = requests.post(self.TV_SHOWS_SEARCH_API, data={"query": self.title})
        if (response.status_code == 200):
            url = response.json()["found"][0]["linkName"]
            webbrowser.open(self.SUBTITLE_PAGE.format(url=url, season=self.season))
        else:
            raise Exception(f"Error while searching a subtitle for {self.title}")
    # ---------------------------------------------- #

    def get_subtitle_url(self) -> str:        
        while True:
            sub_url = input("Subtitle URL: ").strip()
            if (sub_url.startswith("https://api.subsource.net/api/downloadSub/")):
                return sub_url
            else:
                cprint(" Invalid URL", color="red")
    # ---------------------------------------------- #

    def download_subtitle(self, sub_url: str):
        # download subtitle ".zip" file
        response = requests.get(sub_url, headers=self.headers)
        if (response.status_code == 200):
            with open(self.zip_file, "wb") as f:
                f.write(response.content)
        else:
            raise Exception("Failed to download subtitle file!")

        # extract subtitle files
        with zipfile.ZipFile(self.zip_file, "r") as zip_ref:
            zip_ref.extractall(self.subs_path)
            files = glob("*.srt", root_dir=self.subs_path)

            if (len(self.episodes) != len(files)):
                raise Exception(f"Subtitles files [{len(files)}] don't match episodes number [{len(self.episodes)}]")

            for episode, file, in zip(self.episodes, files):
                ofile = os.path.join(self.subs_path, file)
                nfile = os.path.join(self.subs_path, episode+".srt")
                os.rename(ofile, nfile)
            
            # remove ".zip" file
            os.remove(self.zip_file)
# --------------------------------------------------------------------- #

if (__name__ == "__main__"):
    try:
        _, vtype, url, title, season = sys.argv

        if (vtype == "Movie"):
            subtitles = MoviesSubtitles(title)
            subtitles.open_subtitles_search()

            sub_url = subtitles.get_subtitle_url()
            subtitles.download_subtitle(sub_url)
            quit()
        
        elif (vtype == "TV"):
            subtitles = TvShowsSubtitles(url, title, int(season))
            subtitles.open_subtitles_search()
            subtitles.get_episodes()

            sub_url = subtitles.get_subtitle_url()
            subtitles.download_subtitle(sub_url)
            quit()
    
    except Exception as e:
        cprint(e, color="red")
        traceback.print_exc()
        input()
# --------------------------------------------------------------------- #
