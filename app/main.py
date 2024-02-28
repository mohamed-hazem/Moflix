# Utils
from utils_config import *
from utils import *

# App modules
from capture_stage import capture_stage
from download import get_quality, get_segments, download
from recover_merge import check_missing, merge
from movies_subtitles import subtitle
# ================================================== #

# Change working directory
os.chdir(os.path.dirname(__file__))
# -------------------------------------------------- #

# Getting arguments
if (len(sys.argv) != 8):
    input(colored(" - Missing Arguments", "light_red"))
    exit()
else:
    _, url, vtype, name, year, season, episodes, method = sys.argv
# -------------------------------------------------- #

try:
    if (method == "main"):
        # -- Main -- #

        # id
        vid = url.split("-")[-1]

        # title, season and episodes
        if (vtype == "Movie"):
            title = f"{name} ({year})".replace(":", "")
            url = url.replace("/movie/", "/watch-movie/")

        elif (vtype == "TV"):
            title = name.replace(":", "")
            url = url.replace("/tv/", "/watch-tv/")
            season = int(season)
            episodes = get_episodes(episodes)
    # -------------------------------------------------- #

        # Show title
        main_title = title if (vtype == "Movie") else f"{title} S{str(season).zfill(2)}"
        show_title(main_title, c="light_yellow")

        # Capture m3 urls, then stage items
        capture_stage(url, vid, vtype, title, season, episodes)
    # -------------------------------------------------- #

        # Get staged items
        with open(STAGE_FILE, "r") as f:
            staged_item: dict = json.loads(f.read())[vid]
    # -------------------------------------------------- #
    
    elif (method == "manual_main"):
        # -- Manual Main -- #
        close_browser()

        with open(STAGE_FILE, "r") as stage_file:
            staged_items: dict = json.loads(stage_file.read())
        
        if (staged_items == {}):
            show_title("No items to download", c="light_green")
            quit()
    # -------------------------------------------------- #
        
        # Choose item to download
        ids = list(staged_items.keys())
        if (len(ids) > 1):
            for i, vid in enumerate(ids):
                item = staged_items[vid]
                if (item["type"] == "TV"):
                    eps = f"- ({len(list(item.keys())[3:])} Episodes)"
                else:
                    eps = ""
                print(f" [{i+1}] {item['title']} {eps}")
                
            dl = int(input("\n What do you wanna download?: "))-1
        else:
            dl = 0

        vid = ids[dl]
        staged_item = staged_items[vid]
    # -------------------------------------------------- #

    # -- Continue to download the staged item -- # 

    # If there are more than 1 episode, choose what to download
    dl_titles = list(staged_item.keys())[3:]
    if (len(dl_titles) > 1):
        print("\n - Staged items:")
        for i, item in enumerate(dl_titles):
            print(f" [{i+1}] {item}")
        indices = get_episodes(input("\n What do you wanna download?: "))
        dl_titles = dl_titles[indices[0]: indices[1]]
    # -------------------------------------------------- #

    # Loop through all items to be downloaded
    for dl_title in dl_titles:
        m3_url = staged_item[dl_title]

        # Get quality [Unstage file & Quit if user didn't choose quality]
        quality = get_quality(m3_url)
        if (quality is None):
            unstage(vid, dl_title)
            quit()

        segments = get_segments(m3_url, quality)
        path, tmp_path, tmp_exists = init_files(staged_item, dl_title)

        # Download segments
        show_title(f"Downloading {dl_title}", a="-", n=10)
        if (tmp_exists):
            missing_segments = check_missing(segments, tmp_path)
            if (missing_segments):
                download(missing_segments, m3_url, tmp_path, dl_title, quality, len(segments))
        else:
            download(segments, m3_url, tmp_path, dl_title, quality)
        print()

        # Download subtitle
        if (staged_item["type"] == "Movie"):
            threading.Thread(target=lambda: subtitle(dl_title)).start()

        # Merge segments & Recover missing ones
        while True:

            # check missing segments
            missing_segments = check_missing(segments, tmp_path)

            if (missing_segments == False):
                print(colored("\r Merging Segments ...".ljust(LPAD), "light_green"), end="")
                merge(path, tmp_path, dl_title)
                break
            else:
                download(missing_segments, m3_url, tmp_path, dl_title, quality, recover=True)

        # Unstage downloaded item
        unstage(vid, dl_title)
        print("\r", end="")
        show_title(f"[{dl_title}] Downloaded Successfully", n=5, c="light_green")
    # -------------------------------------------------- #

    # Check if it's a start of season to download subtitles
    if (vtype == "TV" and (episodes[0] is None or episodes[0] == 0)):
        d_sub = input(f" Do you wanna download subtitle for {title} S{str(season).zfill(2)}? (y/n): ").strip().lower()
        if (d_sub == "y"):
            run_python("tvshows_subtitle.py", args=[url, name, str(season)])
    # -------------------------------------------------- #
    quit()
    # -------------------------------------------------- #

except Exception as e:
    input(colored(e, "light_red"))
# -------------------------------------------------- #