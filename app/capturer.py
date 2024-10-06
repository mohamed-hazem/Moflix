# Utils
from root_config import *
from utils import *

# Modules
import requests
from selectolax.parser import HTMLParser
import webbrowser
import ctypes
# ===================================================================== #

class Fiddler:
    FIDDLER_PATH = os.path.join(ROOT, APP, "fiddler")
    FIDDLER_TMP_REQUESTS = os.path.join(FIDDLER_PATH, "requests", "requests_number.txt")
    FIDDLER_TMP_REQUESTS_FILE = os.path.join(FIDDLER_PATH, "requests", "{i}.txt")

    # wait for Fiddler to start
    def wait_for_fiddler(self):
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible

        def foreach_window(hwnd, lParam):
            if IsWindowVisible(hwnd):
                length = GetWindowTextLength(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                windows.append(buff.value)
            return True

        while True:
            windows = []
            EnumWindows(EnumWindowsProc(foreach_window), 0)

            if ("Progress Telerik Fiddler Classic" in windows):
                print("\r".ljust(LINE_WIDTH))
                return

            print(f"\r Waiting for Fiddler...", end="", flush=True)
            time.sleep(0.5)
    # ---------------------------------------------- #

    # get the captured url with fiddler, if found
    def get_captured_url(self, tmp_file: str, title: str, c=0) -> str:
        # base case
        if (c == 300):
            cprint(f"\r {title.ljust(LINE_WIDTH)}", "light_red")
            return None
        
        cprint(f"\r {title} - {c} checking ...", "white", end="", flush=True)
        if (os.path.isfile(tmp_file)):
            with open(tmp_file, "r") as f:
                url = f.read()
            os.remove(tmp_file)
                
            cprint(f"\r {title.ljust(LINE_WIDTH)}", "light_green")
            return url
        
        else:
            time.sleep(0.2)
            return self.get_captured_url(tmp_file, title, c=c+1)
    # ---------------------------------------------- #

    # capture m3u8 urls
    def capture_urls(self, watch_urls: dict[str, str]) -> dict[str, str]:
        urls = {}
        for i, title in enumerate(watch_urls, start=1):
            w_url = watch_urls[title]

            if (i == 1):
                # write urls number to be captured with Fiddler
                with open(self.FIDDLER_TMP_REQUESTS, "w") as f:
                    f.write(str(len(watch_urls)))
                
                # run Fiddler, and wait for it to start
                subprocess.Popen(os.path.join(self.FIDDLER_PATH, "Fiddler Classic.lnk"), shell=True)
                self.wait_for_fiddler()
            
            # open "watch url" in the browser
            webbrowser.open(w_url)
            minimize_browser()

            # get m3u8 url
            tmp_file = self.FIDDLER_TMP_REQUESTS_FILE.format(i=i)
            url = self.get_captured_url(tmp_file, title)
            if (url): urls[title] = url
                    
        close_browser()
        
        return urls
# --------------------------------------------------------------------- #

class Capturer:
    MOVIES_API = f"{BASE_URL}/ajax/movie/episodes"
    SEASONS_API = f"{BASE_URL}/ajax/season/list"
    EPISODES_API = f"{BASE_URL}/ajax/season/episodes"
    EPISODES_WATCH_API = f"{BASE_URL}/ajax/episode/servers"
    SERVER = 1
    filter_title = lambda _, title: re.sub(r'[\?\\"/\|:"*<>]', "", title)

    def __init__(self, url: str, vid: str, vtype: str, title: str, season: int, episodes: tuple[int]):
        self.url = url
        self.vid = vid
        self.vtype = vtype
        self.title = title
        self.season = season
        self.episodes = episodes

        self.watch_urls = {}
        self.m3u8_urls = {}
    # ---------------------------------------------- #

    # get watch urls
    def get_watch_urls(self):
        if (self.vtype == "Movie"):
            page = HTMLParser(requests.get(f"{self.MOVIES_API}/{self.vid}").content)
            w_url = BASE_URL + page.css("a.nav-link")[self.SERVER-1].attributes["href"]
            self.watch_urls[self.filter_title(self.title)] = w_url

        elif (self.vtype == "TV"):
            s_page = HTMLParser(requests.get(f"{self.SEASONS_API}/{self.vid}").content)
            seasons = s_page.css("a")

            if (len(seasons) >= self.season):
                s_id = seasons[self.season-1].attributes["data-id"] 
                e_page = HTMLParser(requests.get(f"{self.EPISODES_API}/{s_id}").content)

                eps = e_page.css("a")[self.episodes[0]:self.episodes[1]]
                for e in eps:
                    e_title = e.attributes["title"]
                    e_id = e.attributes["data-id"]
                    e_watch_page = HTMLParser(requests.get(f"{self.EPISODES_WATCH_API}/{e_id}").content)
                    e_watch_id = e_watch_page.css("a")[self.SERVER-1].attributes["data-id"]

                    w_url = f"{self.url.replace("/tv/", "/watch-tv/")}.{e_watch_id}"
                    e_name = re.sub(r'Eps (\d+): (.+)', lambda s: f"E{s.group(1).zfill(2)} - {s.group(2)}", e_title)
                    self.watch_urls[self.filter_title(e_name)] = w_url
            else:
                raise Exception(f"Season {self.season} is not found \n{self.title} is {len(seasons)} seasons")
    # ---------------------------------------------- #
        
    # stage items
    def stage(self):
        new_data = {
            self.vid: {
                "type": self.vtype,
                "title": self.title,
                "season": self.season,
                **self.m3u8_urls
            }
        }

        with open(STAGE_FILE, "r+") as f:
            data = f.read()
            data = json.loads(data) if (data) else dict()
            data.update(new_data)
            
            f.seek(0)
            json.dump(data, f)
            f.truncate()
    # -------------------------------------------------- #
    
    # unstage downloaded item
    @staticmethod
    def unstage(vid: str, dl_title: str):
        with open(STAGE_FILE, "r+") as f:
            data: dict = json.load(f)
            item: dict = data[vid]
        
            if (len(item.keys()) > 3):
                item.pop(dl_title)
            
            if (len(item.keys()) == 3):
                data.pop(vid)
            
            f.seek(0)
            json.dump(data, f)
            f.truncate()
# --------------------------------------------------------------------- #