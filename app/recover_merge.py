# Utils
from utils_config import *
from utils import *
# ================================================== #

# Check missing segments
def check_missing(segments, tmp_path):
    dl_segments = os.listdir(tmp_path)
    
    if (len(dl_segments) == len(segments)):
        return False
    else:
        segments_dict = {seg.split("-")[1]: seg for seg in segments}
        dl_segments_dict = {seg.split("-")[1]: seg for seg in dl_segments}

        missing_segments = [segments_dict[s] for s in segments_dict.keys() if s not in dl_segments_dict.keys()]
            
        return missing_segments
# -------------------------------------------------- #

# Merge segments
def merge(path, tmp_path, title):

    # output file
    output_file = os.path.join(path, f"{title}.mp4")
    
    # tmp output parts
    p1 = os.path.join(tmp_path, "p1.ts")
    p2 = os.path.join(tmp_path, "p2.ts")
    
    # rename files with segment number to be sorted
    ts_files = os.listdir(tmp_path)
    for ts_file in ts_files:
        if (ts_file.endswith(".ts")):
            n_ts_file = ts_file.split("-")[1].zfill(4)+".ts"
            os.rename(os.path.join(tmp_path, ts_file), os.path.join(tmp_path, n_ts_file))
    
    # .ts files & seperated to 2 parts
    ts_files = os.listdir(tmp_path)
    mid = len(ts_files) // 2
    ts1 = ts_files[:mid]
    ts2 = ts_files[mid:]

    # merge files function
    def m(files, output, cwd=tmp_path):
        c = ["ffmpeg", "-i", "concat:"+"|".join(files), "-c", "copy", output]
        subprocess.run(c, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    # merging 2 parts, then the whole file
    m(ts1, p1)
    m(ts2, p2)
    m([p1, p2], output_file)

    # remove all tmp files
    shutil.rmtree(tmp_path)
# -------------------------------------------------- #