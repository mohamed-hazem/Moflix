# Modules
import time, re, subprocess, pygetwindow
from termcolor import cprint

# Constants
from root_config import *
from utils.constants import *
# ===================================================================== #

def get_indices(indices: str) -> tuple[int, int]:
    indices = indices.strip()
    
    # check if it's just a digit
    if (indices.isdigit()):
        s = int(indices)
        return s-1, s
    
    # check if it's empty string
    if (indices == ""):
        return None, None

    # extract indices        
    pattern = r"^\s*(\d*)\s*[-,]\s*(\d*)\s*$"
    match = re.fullmatch(pattern, indices)
    if (match):
        s, e = match.groups()
        s = int(s)-1 if (s) else None
        e = int(e)-0 if (e) else None

        # raise an error if start value is greater than end value
        if (s and e) and (s >= e):
            raise Exception(f"Invalid ragne => from {s+1} to {e}")
        
        return s, e
    
    else:
        raise Exception(f"Invalid input => {indices}")
# --------------------------------------------------------------------- #

def choose(text: str, prompt: str, options: list[str], choose_one=True, return_indices=False) -> list | str | int:
    # print options
    print(f" {text}")
    for i, opt in enumerate(options):
        print(f" [{i+1}] {opt}")
    
    # get input
    while True:
        try:
            idx = input(f" {prompt.capitalize()} / (E)xit: ").strip().lower()
            print()
            if (idx in ("e", "exit")): sys.exit()

            idx = get_indices(idx)
            choices = options[idx[0]: idx[1]]
            
            assert choices
            if (choose_one): assert len(choices) == 1

            results = idx if (return_indices) else choices
            return results[0] if (choose_one) else results
        
        except SystemExit:
            sys.exit()
        except:
            cprint("Invalid choice", "light_red")
# --------------------------------------------------------------------- #

# run python file
def run_python(file_name: str, args=[]):
    python_file = [os.path.join(ROOT, APP, file_name)]
    subprocess.Popen(["start", "cmd", "/c", "python"] + python_file + args, shell=True)
# --------------------------------------------------------------------- #

# Browser helpers #
def minimize_browser(w=0.5):
    time.sleep(w)
    while True:
        browser_windows = pygetwindow.getWindowsWithTitle(BROWSER)
        if (browser_windows):
            browser_windows[-1].minimize()
            break
# ---------------------------------------------- #

def close_browser():
    browser_windows = pygetwindow.getWindowsWithTitle(BROWSER)
    if (browser_windows):
        browser_window = browser_windows[-1]
        browser_window.maximize()
        browser_window.close()
# --------------------------------------------------------------------- #

# Print helpers #
def show_step(text: str, color="white", a="=>", nl=True):
    text = f"\r {a} {text.capitalize()}".ljust(LINE_WIDTH)
    cprint(text, color, end="", flush=True)
    if (nl): print()
# ---------------------------------------------- #

def show_title(text: str, color="white", padding_char="=", padding_count=40, nl=True, pl=False):
    if (pl): print("\r".ljust(LINE_WIDTH))

    max_padding = (LINE_WIDTH - len(text) - 2) // 2
    padding_to_add = min(padding_count, max_padding)
    space = max_padding - padding_to_add
    
    text = f"{' '*space}{padding_char*padding_to_add} {text} {padding_char*padding_to_add}{' '*space}"
    cprint(text, color)

    if (nl): print()
# ---------------------------------------------- #

def quit(t=5, color="white"):
    for i in range(t):
        cprint(f"\r Quit in {t-i}s", color=color, end="", flush=True)
        time.sleep(1)
    exit()
# --------------------------------------------------------------------- #