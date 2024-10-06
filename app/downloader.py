# Utils
from root_config import *
from utils import *

# Modules
from dataclasses import dataclass
from glob import glob
import requests, m3u8

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
# ===================================================================== #

@dataclass
class Segment:
    name: str
    url: str
# --------------------------------------------------------------------- #

class Downloader:
    TIMEOUT = 15
    TRIES = 3

    def __init__(self, dl_item: dict[str, str], dl_title: str):
        self.dl_item = dl_item
        self.dl_title = dl_title
        self.m3u8_url = dl_item[dl_title]

        self.segments: list[Segment]
        self.missing_segments: list[Segment]
    # ---------------------------------------------- #
    
    # choose another quality, if settings quality isn't available
    def config_quality(self):
        playlists = m3u8.load(self.m3u8_url).playlists
        playlists = {str(pl.stream_info.resolution[1]): pl.uri for pl in playlists}

        quality = QUALITY
        if (quality not in playlists):
            quality = choose(f"{quality}p isn't available!", prompt="choose quality", options=list(playlists.keys()))
        
        self.m3u8_url = playlists[quality]
    # ---------------------------------------------- #

    # fetch segments from the m3u8 file
    def get_segments(self):    
        playlist = m3u8.load(self.m3u8_url)
        self.segments = [Segment(name=f"seg-{str(n+1).zfill(4)}.ts", url=url) for n, url in enumerate(playlist.files)]
    # ---------------------------------------------- #

    # pre-downloading init files [uid config]
    def init_files(self):
        vtype = self.dl_item["type"]
        title = self.dl_item["title"]
        season = self.dl_item["season"]
        uid = self.dl_title

        if (vtype == "Movie"):
            self.path = os.path.join(MOVIES_DIR, title)

        elif (vtype == "TV"):
            self.path = os.path.join(TVSHOWS_DIR, title, f"Season {season}")
        
        self.tmp_path = os.path.join(self.path, uid)      
        
        os.makedirs(self.tmp_path, exist_ok=True)
    # ---------------------------------------------- #
    
    # just check if there are missing segments
    def __check_missing_segments(self) -> bool:
        dl_segments = glob(pathname="seg*.ts", root_dir=self.tmp_path)
        return (len(dl_segments) != len(self.segments))
    # ---------------------------------------------- #

    # get missing segments to recover
    def __get_missing_segments(self) -> list[str]:
        dl_segments = set(glob(pathname="seg*.ts", root_dir=self.tmp_path))

        if (len(dl_segments) == len(self.segments)) or (len(dl_segments) == 0):
            return []
        
        segments_dict = {s.name: s for s in self.segments}
        diff = segments_dict.keys() - dl_segments

        missing_segments = [segments_dict[i] for i in diff]
        
        return missing_segments
    # ---------------------------------------------- #

    # download segment of different server
    def __dl_seg(self, seg: Segment):
        seg_file = os.path.join(self.tmp_path, seg.name)

        for _ in range(self.TRIES):
            try:
                res = requests.get(seg.url, timeout=self.TIMEOUT)
                with open(seg_file, "wb") as vf:
                    vf.write(res.content)
                return
            except:
                time.sleep(1)
    # ---------------------------------------------- #

    def download(self):
        self.missing_segments = self.__get_missing_segments()
        recover = bool(self.missing_segments)
            
        if (recover):
            download_segments = self.missing_segments
        else:
            download_segments = self.segments
        
        total = len(self.segments)
        init = total - len(download_segments)
        desc = f" {self.dl_title}"
        leave = not recover

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.__dl_seg, segment) for segment in download_segments]
            progress_bar = tqdm(total=total, initial=init, desc=desc, colour="green", unit="vid", leave=leave)
            for _ in as_completed(futures):
                progress_bar.update()
            progress_bar.close()
        
        # execute `download()` recursively, until all segments are downloaded
        if (self.__check_missing_segments()):
            self.download()
# --------------------------------------------------------------------- #