# Utils
from utils_config import *
from utils import *
# ================================================== #

# Get quality
def get_quality(m3_url):
    m3_url = f"{m3_url}/playlist.m3u8"
    m3_master = m3u8.loads(requests.get(m3_url).text)
    playlists = m3_master.data["playlists"]
    qualities = [s["stream_info"]["resolution"].split("x")[1] for s in playlists]

    if (QUALITY in qualities):
        return QUALITY
    else:
        print(f" {QUALITY}p isn't found :(")
        for i, q in enumerate(qualities):
            print(f" [{i+1}] {q}p")
        
        c = input(" Choose quality or exit (e): ")
        if (c.isnumeric()):
            c = int(c)
            quality = qualities[c-1]
        elif (c == "e"):
            return None

    return quality
# -------------------------------------------------- #

# Get segments
def get_segments(m3_url: str, quality):
    m3_url = f"{m3_url}/{quality}/index.m3u8"

    m3_master = m3u8.loads(requests.get(m3_url).text)
    segments = [s["uri"].split("/")[-1] for s in m3_master.data["segments"]]

    return segments
# -------------------------------------------------- #

# Main Download Function #
def download(segments, m3_url, tmp_path, title, quality, total_segments=None, recover=False):
    total_segments = len(segments) if (total_segments is None) else total_segments
    init = total_segments - len(segments)

    def dl_and_save_seg(m3_url, seg, ext, seg_path):
        try:
            r = requests.get(f"{m3_url}/{quality}/{seg}.{ext}", timeout=TIMEOUT)
            with open(seg_path, "wb") as vid:
                vid.write(r.content)
            return True
        except:
            return False
        
    # download a segment
    def dl_seg(seg: str):
        seg_path = os.path.join(tmp_path, seg+".ts")
        seg, ext = seg.split(".")

        # download the segment with the main extenstion
        for _ in range(MAX_TRIES):
            if (dl_and_save_seg(m3_url, seg, ext, seg_path)): return
        
        # download with the other extenstion in case the main failed
        for _ in range(MAX_EXT_TRIES):
            for ext in ALL_EXT:
                if (dl_and_save_seg(m3_url, seg, ext, seg_path)): return

    # download all segments using multi-threading & create a progress bar
    if (recover):
        desc = " Recovering Segments"
        color = "red"
    else:
        desc = f" {title}"
        color = "green"
    leave = (not recover)
    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(dl_seg, segment) for segment in segments]
        for _ in tqdm(as_completed(futures), total=total_segments, initial=init, desc=desc, colour=color, unit="vid", leave=leave):
            pass
# -------------------------------------------------- #