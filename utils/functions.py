# Config
from .config import *
# ================================================== #

# Get episodes range
def get_episodes(episodes: str):
    if (episodes):
        ep = episodes.split("-")
        
        if (len(ep) == 1):
            s = int(ep[0])-1
            return s, s+1
        else:
            s = int(ep[0])-1 if (ep[0]) else None
            e = int(ep[1])-0 if (ep[1]) else None

        return s, e
    else:
        return (None, None)
# -------------------------------------------------- #

# Pre-downloading init files
def init_files(staged_item: dict, dl_title):
    vtype = staged_item["type"]
    title = staged_item["title"]
    season = staged_item["season"]
    uid = staged_item[dl_title].split("/")[4][:5]

    if (vtype == "Movie"):
        path = os.path.join(MOVIES_DIR, title)

    elif (vtype == "TV"):
        show_path = os.path.join(TVSHOWS_DIR, title)
        if not (os.path.isdir(show_path)): os.mkdir(show_path)
        path = os.path.join(TVSHOWS_DIR, title, f"Season {season}")
    
    tmp_path = os.path.join(path, uid)
    tmp_exists = os.path.isdir(tmp_path)

    if not (os.path.isdir(path)): os.mkdir(path)
    if not (tmp_exists): os.mkdir(tmp_path)
    
    return path, tmp_path, tmp_exists
# -------------------------------------------------- #

# Unstage downloaded item
def unstage(vid, dl_title):
    with open(STAGE_FILE, "r+") as f:
        staged_data = json.loads(f.read())
    
        item = staged_data[vid]
        if (len(item.keys()) > 3):
            item.pop(dl_title)
        
        if (len(item.keys()) == 3):
            staged_data.pop(vid)
        
        f.seek(0)
        json.dump(staged_data, f)
        f.truncate()
# -------------------------------------------------- #

# Minimize browser
def minimize_browser(w=0.5):
    sleep(w)
    while True:
        browser_windows = pygetwindow.getWindowsWithTitle(BROWSER)
        if (browser_windows):
            browser_windows[-1].minimize()
            break

# Maximize browser
def close_browser():
    browser_windows = pygetwindow.getWindowsWithTitle(BROWSER)
    if (browser_windows):
        browser_window = browser_windows[-1]
        browser_window.maximize()
        browser_window.close()
# -------------------------------------------------- #

# Check if `Fiddler` is started
def get_running_apps():
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible

    windows = []
    def foreach_window(hwnd, lParam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            windows.append(buff.value)
        return True

    EnumWindows(EnumWindowsProc(foreach_window), 0)
    
    return windows        

def wait_for_fiddler():
    while True:
        print(f"\r Waiting for Fiddler...", end="", flush=True)

        running_apps = get_running_apps()
        if ("Progress Telerik Fiddler Classic" in running_apps):
            print("\r".ljust(LPAD))
            return
        
        sleep(0.5)
# -------------------------------------------------- #

# Run python file
def run_python(file_name, args=[]):
    python_file = [os.path.join(ROOT, APP, file_name)]
    subprocess.Popen(START_PYTHON + python_file + args, shell=True)
# -------------------------------------------------- #

# Filter file names
def filter_name(name: str):
    return "".join(filter(lambda c: c not in SHIT_CHARS, name))
# -------------------------------------------------- #

# Style functions
def show_step(msg: str, a="-", c="white"):
    msg = f" {a} {msg.capitalize()}"
    print(colored(msg, c))

def show_title(msg: str, a="=", n=35, nl=True, c="white"):
    s = (116 - len(msg)) // 2
    print("\r", " "*LPAD)
    msg = f"{(a*n).rjust(s)} {msg} {a*n}"
    print(colored(msg, c))
    if (nl): print()

def quit(t=5, c="white"):
    for i in range(t):
        print(colored(f"\r Quit in {t-i}s", c), end="", flush=True)
        sleep(1)
    exit()
# -------------------------------------------------- #