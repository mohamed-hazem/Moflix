# Modules
import os, time, json, subprocess, webbrowser, pyperclip
from termcolor import cprint
from win32com.client import Dispatch
# ===================================================================== #

ROOT = os.path.dirname(os.path.dirname(__file__))
APP = "app"
WEB_APP = "web_app"
FIDDLER_PATH = os.path.join(ROOT, APP, "fiddler")

POWERSHELL = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
CONFIG_DOC = "https://docs.telerik.com/fiddler/configure-fiddler/tasks/decrypthttps"
# --------------------------------------------------------------------- #

os.chdir(ROOT) # idk if it matters
# --------------------------------------------------------------------- #

# Helpers
def write(text: str, color="light_yellow", t=1):
    ct = t / len(text)
    print(" ", end="")
    for c in text:
        cprint(c, color=color, end="", flush=True)
        time.sleep(ct)
    print()

def line_next(n=75, next=True):
    print("="*n)
    if (next):
        cprint("\r Press enter for the next step", color="light_green", end="")
    input()
    print("="*n)
# --------------------------------------------------------------------- #

# Welocome
write(" === Welcome to Moflix ===")

# Install choco & ffmpeg
write("[1] Install chocolatey & ffmpeg")

try:
    subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    write("ffmpeg is already installed", color="light_green")

except subprocess.CalledProcessError:
    CHOCO_SETUP = "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    subprocess.run([POWERSHELL, "-Command", f'Start-Process powershell -ArgumentList "-Command {CHOCO_SETUP}" -Verb RunAs'])

    FFMPEG_SETUP = "choco install ffmpeg"
    subprocess.run([POWERSHELL, "-Command", f'Start-Process powershell -ArgumentList "-Command {FFMPEG_SETUP}" -Verb RunAs'])
line_next()
# --------------------------------------------------------------------- #

# Setup settings
write("[2] Setup settings")

settings = {
    "QUALITY": "1080",
    "MOVIES_DIR": "E:\\Movies",
    "TVSHOWS_DIR": "E:\\TV Shows",
    "BROWSER": "Google Chrome"
}
with open(os.path.join(ROOT, "setup", "settings.json"), "w") as settings_file:
    json.dump(settings, settings_file)

write(" Open up `settings.json`")
write("- Make sure that you have [Movies] & [TV Shows] folders in any disk", color="white")
write("- Set Quality [1080, 720, 480]", color="white")
write("- Set your default browser [default => Google Chrome]", color="white")
line_next()
# --------------------------------------------------------------------- #

# Install "Fiddler"
write("[3] Install Fiddler")

fiddler_installed = False
APPDATA = os.environ.get("APPDATA")
if (APPDATA):
    FIDDLER_INSTALLATION_PATH = os.path.join(os.path.dirname(APPDATA), "Local", "Programs", "Fiddler")
    if (os.path.exists(FIDDLER_INSTALLATION_PATH)):
        fiddler_installed = True
        write("Fiddler is already installed", color="light_green")

if (fiddler_installed == False):
    subprocess.run(os.path.join(ROOT, "setup", "FiddlerSetup.exe"), shell=True)
line_next()
# --------------------------------------------------------------------- #

# Configure "Fiddler"
write("[4] Configure Fiddler to decrypt HTTPS traffic")
write(f"Go through configuration doc -> [{CONFIG_DOC}]")
webbrowser.open(CONFIG_DOC)

subprocess.run(os.path.join(FIDDLER_PATH, "Fiddler Classic.lnk"), shell=True)
line_next()
# --------------------------------------------------------------------- #

# Generate "Fiddler" script
write("[5] Generate Fiddler Script")
write("Make sure you closed Fiddler")

with open(os.path.join(FIDDLER_PATH, "Fiddler Script.txt"), "r+") as f:
    PATH = os.path.join(FIDDLER_PATH, "requests").replace("\\", "\\\\")
    path_line_start = "static var PATH: String"

    # get PATH line
    lines = f.readlines()
    for i, l in enumerate(lines):
        if (l.strip().startswith(path_line_start)):
            lines[i] = f'\t{path_line_start} = "{PATH}";\n'
    
    # write new code
    f.seek(0)
    f.writelines(lines)
    f.truncate()
    pyperclip.copy("".join(lines))
    
    # open up 'Fiddler Script Editor'
    write(" Go to Rules -> Customize Rules")
    write("\n Replace the code in the editor with the code that's already has been generated and copied", color="white")
    subprocess.run(os.path.join(FIDDLER_PATH, "Fiddler Classic.lnk"), shell=True)

line_next()
# --------------------------------------------------------------------- #

# Desktop Shourtcut
write("[6] Create Desktop Shortcut")
shortcut_path = os.path.join(os.path.expanduser("~"), "Desktop", "Moflix.lnk")
app_path = os.path.join(ROOT, WEB_APP, "app.py")
icon_path = os.path.join(ROOT, WEB_APP, "static", "icon.ico")

shell = Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(shortcut_path)
shortcut.TargetPath = app_path
shortcut.IconLocation = icon_path
shortcut.Save()
# --------------------------------------------------------------------- #

write(f"All set now, go enjoy this useless app YOU LIFELESS PIECE OF SHIT", t=3, color="light_green")
line_next(next=False)
# --------------------------------------------------------------------- #