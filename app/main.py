# Utils
from root_config import *
from utils import *

# Modules
import traceback

from app.capturer import Capturer, Fiddler
from app.downloader import Downloader
from app.merger import Merger
# ===================================================================== #

class Main:
    def __init__(self):
        _, self.url, self.vtype, self.name, self.year, self.season, self.episodes, self.method = sys.argv
        self.subtitle = False
    # ---------------------------------------------- #

    def preprocess_inputs(self):
        if (self.vtype == "Movie"):
            self.title = f"{self.name} ({self.year})"
            self.main_title = self.title
            self.subtitle = True
        
        elif (self.vtype == "TV"):
            self.title = self.name
            self.main_title = f"{self.title} S{self.season.zfill(2)}"
            
            self.season = int(self.season)
            self.episodes = get_indices(self.episodes)
            
            if (self.episodes[0] in (None, 0)):
                self.subtitle = True
    # ---------------------------------------------- #

    def get_dl_item(self) -> dict[str, str]:
        with open(STAGE_FILE, "r") as f:
            staged_items: dict = json.load(f)
        
        if (not staged_items):
            raise Exception("No items to download")
        
        elif (self.method == "open-staged"):            
            options = [staged_items[i]["title"] for i in staged_items]                
            if (len(options) == 1):
                idx = 0
            else:
                idx = choose(text="", options=options, prompt="what do you want to download", return_indices=True)
            
            self.vid = list(staged_items.keys())[idx]

        dl_item = staged_items[self.vid]
        
        return dl_item
    # ---------------------------------------------- #

    def run(self):
        self.preprocess_inputs()

        # capture, and stage the item
        if (self.method == "auto"):
            show_title(self.main_title, color="light_yellow")

            self.vid = self.url.split("-")[-1]
            capturer = Capturer(self.url, self.vid, self.vtype, self.title, self.season, self.episodes)
            capturer.get_watch_urls()
            capturer.m3u8_urls = Fiddler().capture_urls(watch_urls=capturer.watch_urls)
            capturer.stage()
        
        # get item to download
        dl_item = self.get_dl_item()

        # get titles (items) to download
        dl_titles = list(dl_item.keys())[3:]
        if (len(dl_titles) > 1):
            dl_titles = choose(text="Episodes:", prompt="choose episodes to download e.g. 6, 9",
                                options=dl_titles, choose_one=False)

        # loop through titles to download them
        for dl_title in dl_titles:

            # download item segments
            show_title(text=f"Downloading {dl_title}", padding_char="-", padding_count=20)
            downloader = Downloader(dl_item, dl_title)
            downloader.config_quality()
            downloader.get_segments()
            downloader.init_files()
            downloader.download()

            # merge downloaded segments
            show_step(text="merging segments ...", color="light_green", nl=False)
            Merger(downloader.tmp_path, dl_title).merge()

            # unstage downloaded item
            Capturer.unstage(self.vid, dl_title)
            show_title(f"[{dl_title}] Downloaded Successfully", padding_char="-", padding_count=20,
                        color="light_green", pl=True)
            
            # download subtitles
            if (self.subtitle):
                decision = input(f"Download subtitle for {self.main_title}? (y)es/(no): ").strip().lower()
                if (decision in ("y", "yes", "")):
                    run_python("subtitles.py", args=[self.vtype, self.url, self.title, str(self.season)])
            quit()
# --------------------------------------------------------------------- #

if (__name__ == "__main__"):
    try:
        Main().run()
    except Exception as e:
        cprint(e, color="red")
        traceback.print_exc()
        input()
# --------------------------------------------------------------------- #